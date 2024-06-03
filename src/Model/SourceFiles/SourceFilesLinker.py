from Model.SourceFiles.SourceFile import SourceFile
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from settings_namespace import GENERATED_FILES


class SourceFilesLinker:
    HARD_LINK_NAME:str='main.tex'
    def __init__(self, settings: dict[str, str]):
        self.settings = settings
        self.source_files_manager = SourceFilesManager(settings)

    def _link(self, linkage_method: callable, source_files_instances: list[SourceFile]) -> tuple[bool, bool]:
        """
        Method links following source files with inputs marks, linking assume that files construct stack
        :return: bool - were able to link all marks connected with first source file as parent,
        bool - was not error during execution
        """
        if len(source_files_instances) == 0:
            return True, True

        # list[element with inputs, unsatisfied inputs]
        first_source_file: SourceFile = source_files_instances.pop(0)
        files_stack: list[tuple[SourceFile, list[str]]] = [
            (first_source_file, first_source_file.get_all_marks())]

        # if first stack layer hasn't any marks to input, return
        if files_stack[0][0] == []:
            return True, True

        while files_stack != []:
            current_instance, marks = files_stack.pop()

            if marks != [] and source_files_instances!=[]:
                files_stack.append((current_instance, marks))
                next_file: SourceFile = source_files_instances.pop(0)
                files_stack.append((next_file, next_file.get_all_marks()))
            elif marks != [] and source_files_instances==[]:
                return False, True
            elif len(files_stack)>0:
                uncovered_instance, uncovered_marks = files_stack.pop()
                if not linkage_method(uncovered_instance, uncovered_marks[0], current_instance):
                    return False, False
                uncovered_marks.pop(0)
                files_stack.append((uncovered_instance, uncovered_marks))

        return True, True

    def soft_link(self) -> tuple[bool, bool]:
        def linkage(source_file: SourceFile, mark: str, file_instance: SourceFile) -> bool:
            return source_file.replace_input(mark, file_instance.filepath)

        return self._link(linkage, self.source_files_manager.create_source_files_instances())

    def hard_link(self) -> tuple[bool, bool]:
        def linkage(source_file: SourceFile, mark: str, file_instance: SourceFile) -> bool:
            was_successful, content = file_instance.read_content_of_file()
            if not was_successful:
                return False
            return source_file.hard_replace(mark, content)

        basic_source_files: list[SourceFile]=self.source_files_manager.create_source_files_instances()
        changed_source_files: list[SourceFile]=[]
        for basic_file in basic_source_files:
            was_success, file_path=basic_file.create_copy_to_another_directory(self.settings[GENERATED_FILES])
            if not was_success:
                return False, False
            else:
                changed_source_files.append(SourceFile(file_path))

        if basic_source_files==[]:
            return True, True

        initial_result= self._link(linkage, list(changed_source_files))

        change_name_result:bool=changed_source_files[0].rename(SourceFilesLinker.HARD_LINK_NAME)
        if not change_name_result:
            return False,False

        for changed_file in changed_source_files[1:]:
            remove_result: bool=changed_file.remove()
            if not remove_result:
                return False, False

        return initial_result


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}
    linker: SourceFilesLinker = SourceFilesLinker(local_settings)
    # print(linker.soft_link())
    print(linker.hard_link())
