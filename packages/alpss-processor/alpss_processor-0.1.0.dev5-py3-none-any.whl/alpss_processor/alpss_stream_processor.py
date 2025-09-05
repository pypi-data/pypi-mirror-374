"""A DataFileStreamHandler that triggers some arbitrary local code when full files are available"""

import datetime
from openmsistream.data_file_io.actor.data_file_stream_processor import (
    DataFileStreamProcessor,
)
from alpss.commands import alpss_main_with_config
import json
from openmsistream.girder.girder_upload_stream_processor import (
    GirderUploadStreamProcessor,
)
from openmsistream.data_file_io.entity.data_file import DataFile
from openmsistream.data_file_io.entity.download_data_file import DownloadDataFileToMemory
from pathlib import Path
import pickle
import numpy as np
from io import BytesIO
import pandas as pd


class ALPSStreamProcessor(DataFileStreamProcessor):
    """
    A class to consume :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk` messages
    into memory and perform some operation(s) when entire files are available.
    This is a base class that cannot be instantiated on its own.

    :param config_path: Path to the config file to use in defining the Broker connection
        and Consumers
    :type config_path: :class:`pathlib.Path`
    :param topic_name: Name of the topic to which the Consumers should be subscribed
    :type topic_name: str
    :param output_dir: Path to the directory where the log and csv registry files should be kept
        (if None a default will be created in the current directory)
    :type output_dir: :class:`pathlib.Path`, optional
    :param mode: a string flag determining whether reconstructed data files should
        have their contents stored only in "memory" (the default, and the fastest),
        only on "disk" (in the output directory, to reduce the memory footprint),
        or "both" (for flexibility in processing)
    :type mode: str, optional
    :param datafile_type: the type of data file that recognized files should be reconstructed as.
        Default options are set automatically depending on the "mode" argument.
        (must be a subclass of :class:`~.data_file_io.DownloadDataFile`)
    :type datafile_type: :class:`~.data_file_io.DownloadDataFile`, optional
    :param n_threads: the number of threads/consumers to run
    :type n_threads: int, optional
    :param consumer_group_id: the group ID under which each consumer should be created
    :type consumer_group_id: str, optional
    :param filepath_regex: If given, only messages associated with files whose paths match
        this regex will be consumed
    :type filepath_regex: :type filepath_regex: :func:`re.compile` or None, optional

    :raises ValueError: if `datafile_type` is not a subclass of
        :class:`~.data_file_io.DownloadDataFileToMemory`, or more specific as determined
        by the "mode" argument
    """

    def __init__(
        self,
        config,
        topic_name,
        alpss_config_path,
        **kwargs,
    ):

        self.url = kwargs.pop("girder_api_url")
        self.api_key = kwargs.pop("girder_api_key")
        self.girder_root_folder_id = kwargs.pop("girder_root_folder_id")

        self.girder_uploader = GirderUploadStreamProcessor(self.url, self.api_key, config_file=config, topic_name=topic_name, girder_root_folder_id=self.girder_root_folder_id, delete_on_disk_mode=False)

        super().__init__(config_file=config, topic_name=topic_name, **kwargs)

        self.alpss_config_path = alpss_config_path
        try:
            with open(self.alpss_config_path, "r") as f:
                self.alpss_config = json.load(f)
        except Exception as e:
            raise Exception(f"Unexpected error while loading ALPSS config: {str(e)}")

    def _process_downloaded_data_file(self, datafile, lock):
        """
        Perform some arbitrary operation(s) on a given data file that has been fully read
        from the stream. Can optionally lock other threads using the given lock.

        Not implemented in the base class.

        :param datafile: A :class:`~.data_file_io.DownloadDataFileToMemory` object that
            has received all of its messages from the topic
        :type datafile: :class:`~.data_file_io.DownloadDataFileToMemory`
        :param lock: Acquiring this :class:`threading.Lock` object would ensure that
            only one instance of :func:`~_process_downloaded_data_file` is running at once
        :type lock: :class:`threading.Lock`

        :return: None if processing was successful, an Exception otherwise
        """
        with lock:
            try:
                self.alpss_config["bytestring"] = datafile.bytestring # add 'bytestring' to the config that points it to the input
                self.alpss_config["filepath"] = datafile.filename
                fig, alpss_results = alpss_main_with_config(self.alpss_config)
                for result_name, result in alpss_results.items():
                    if result_name == "results":
                        continue
                    self.girder_uploader._girder_client.uploadFileToFolder(self.girder_root_folder_id, result[-1])
                    if self.mode == "disk" and self.delete_on_disk_mode:
                        msg = self.safe_delete_file(Path(result[-1]))
                        msg += " (artefact generated from ALPSS)"
                        self.logger.debug(msg)
            except Exception as e:
                print(f"Caught an exception: {e}")
        return None

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        girder_args, girder_superkwargs = (
            GirderUploadStreamProcessor.get_command_line_arguments()
        )
        args = [
            *superargs,
        ]
        args.extend(girder_args)
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        """
        Run the stream-processed analysis code from the command line
        """
        # make the argument parser
        parser = cls.get_argument_parser()
        parser.add_argument(
            "--alpss_config_path", help="Path to the config file containing ALPSS parameter"
        )
    
        args = parser.parse_args(args=args)

        # make the stream processor
        alpss_analysis = cls(
            args.config,
            args.topic_name,
            args.alpss_config_path,
            delete_on_disk_mode=args.delete_on_disk_mode,
            filepath_regex=args.download_regex,
            mode=args.mode,
            n_threads=args.n_threads,
            update_secs=args.update_seconds,
            consumer_group_id=args.consumer_group_id,
            girder_api_url=args.girder_api_url,
            girder_api_key=args.girder_api_key,
            girder_root_folder_id=args.girder_root_folder_id,
        )

        # start the processor running (returns total number of messages read, processed, and names of processed files)
        run_start = datetime.datetime.now()
        msg = (
            f"Listening to the {args.topic_name} topic for flyer image files to analyze"
        )
        alpss_analysis.logger.info(msg)
        (
            n_read,
            n_processed,
            processed_filepaths,
        ) = alpss_analysis.process_files_as_read()
        alpss_analysis.close()
        run_stop = datetime.datetime.now()
        # shut down when that function returns
        msg = "ALPSS analysis stream processor "
        if args.output_dir is not None:
            msg += f"writing to {args.output_dir} "
        msg += "shut down"
        alpss_analysis.logger.info(msg)
        msg = f"{n_read} total messages were consumed"
        if len(processed_filepaths) > 0:
            msg += f", {n_processed} messages were successfully processed,"
            msg += f" and the following {len(processed_filepaths)} file"
            msg += " " if len(processed_filepaths) == 1 else "s "
            msg += f"had analysis results added to {args.db_connection_str}"
        else:
            msg += f" and {n_processed} messages were successfully processed"
        msg += f" from {run_start} to {run_stop}"
        for fn in processed_filepaths:
            msg += f"\n\t{fn}"
        alpss_analysis.logger.info(msg)


def main(args=None):
    ALPSStreamProcessor.run_from_command_line(args=args)

if __name__ == "__main__":
    main()
