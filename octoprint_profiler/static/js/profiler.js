/*
 * View model for OctoPrint-Profiler
 *
 * Author: Gaston Dombiak
 * License: AGPLv3
 */
$(function() {
    function ProfilerViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        self.settingsViewModel = parameters[0];

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: ProfilerViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel" ],
        // Elements to bind to, e.g. #settings_plugin_profiler, #tab_plugin_profiler, ...
        elements: [ "#settings_plugin_profiler" ]
    });
});
