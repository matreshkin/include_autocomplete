"""Listens to completion queries in #include statements."""

import os
import collections
import json
import sublime
import sublime_plugin

import logging


def InitializeMainLogger(main_logger):
    """Apply required settings to the main logger.
    """
    if not main_logger.hasHandlers():
        # Must be set to lowest level to get total freedom in handlers
        main_logger.setLevel(logging.DEBUG)

        # Disable log duplications when reloading
        main_logger.propagate = False

        # Create / override console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '[Include Autocomplete / %(levelname)s] %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to logger
        main_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)
InitializeMainLogger(logger)


# Include setting keys
STR_INCL_SETTINGS = 'include_autocomplete_settings'
STR_INCL_SETTING_INCL_LOC = 'include_locations'
STR_INCL_SETTING_IL_PATH = 'path'
STR_INCL_SETTING_IL_PREFIX = 'prefix'
HEADER_EXT = (".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp")

class IncludeAutoComplete(sublime_plugin.EventListener):
    """Listens to completion queries in "#include" statements."""

    def __init__(self):
        self.reload()

    def get_include_locations_from_project_data(self):
        result = []
        project_data = sublime.active_window().project_data()
        if project_data is None:
            return result
        if project_data:
            incl_settings = project_data.get(STR_INCL_SETTINGS, None)
            if incl_settings is None:
                return result
        if incl_settings is None:
            return result
        incl_locations = incl_settings.get(STR_INCL_SETTING_INCL_LOC, None)
        if incl_locations is None:
            return result
        if isinstance(incl_locations, collections.Sequence):
            for loc in incl_locations:
                path = loc.get(STR_INCL_SETTING_IL_PATH, None)
                if not path:
                    continue
                prefix = loc.get(STR_INCL_SETTING_IL_PREFIX, None)
                path = sublime.expand_variables(path, sublime.active_window().extract_variables())
                path = os.path.abspath(path)
                result.append((path, prefix))
        return result

    def reload(self):
        include_folders = self.get_include_locations_from_project_data()
        self.completions = []
        for include_root, prefix in include_folders:
            base_len = len(include_root) + 1
            for path, dirs, files in os.walk(include_root, followlinks = True):
                for file in files:
                    if file.endswith(HEADER_EXT):
                        file_path = os.path.join(path, file)
                        file_dir = os.path.basename(path)
                        file_path = file_path[base_len:]
                        if prefix is not None:
                            file_path = os.path.join(prefix, file_path)
                        self.completions.append(("%s\t%s" % (file, file_dir), file_path))
        print(self.completions)

    def on_query_completions(self, view, prefix, locations):
        if len(locations) != 1:
            return None

        if not view.match_selector(locations[0],
                                   "meta.preprocessor.include & "
                                   "(string.quoted.other | "
                                   "string.quoted.double)"):
            return None

        completions = self.completions
        if len(completions) > 0:
            print(completions)
            return (completions,
                    sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        return None

    def on_window_command(self, window, command_name, args):
        if command_name == "refresh_folder_list":
            self.reload()
        return None
