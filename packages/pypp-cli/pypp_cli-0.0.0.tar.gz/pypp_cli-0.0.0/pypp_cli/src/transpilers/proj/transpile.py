from pathlib import Path

from pypp_cli.src.transpilers.proj.create_all_data import (
    AllData,
    create_all_data,
)
from pypp_cli.src.transpilers.proj.other.file_loader import (
    TimeStampsFile,
)
from pypp_cli.src.other.pypp_paths.do import DoPyppPaths


def pypp_transpile(paths: DoPyppPaths) -> list[Path]:
    a: AllData = create_all_data(paths)

    a.cpp_project_initializer.initialize_of_cpp_dir_is_dirty()

    src_changes, main_changes = a.file_change_cltr.calc_changes()

    a.cmake_lists_writer.write(main_changes.ignored_file_stems)

    files_deleted: int = a.cpp_and_h_file_deleter.delete_files(
        [
            src_changes.deleted_files,
            main_changes.deleted_files,
            src_changes.changed_files,
            main_changes.changed_files,
        ]
    )

    ret = a.main_and_src_transpiler.transpile(src_changes, main_changes, files_deleted)

    a.timestamps_saver.save(
        TimeStampsFile(main_changes.new_timestamps, src_changes.new_timestamps)
    )

    return ret
