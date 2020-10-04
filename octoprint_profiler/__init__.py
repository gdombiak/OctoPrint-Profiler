# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import yappi
from datetime import datetime
from octoprint.events import Events


class ProfilerPlugin(octoprint.plugin.SettingsPlugin,
					 octoprint.plugin.AssetPlugin,
					 octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.EventHandlerPlugin):

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/profiler.js"],
			css=["css/profiler.css"],
			less=["less/profiler.less"]
		)

	##~~ EventHandlerPlugin mixin

	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			# Start Profiling
			self._logger.info("Profiling started")
			yappi.start()
		if event == Events.PRINT_DONE or event == Events.PRINT_CANCELLED:
			# Stop profiling and save statistics to a file for later analysis
			now__isoformat = datetime.now().isoformat()

			file_name = 'profiler-func-' + now__isoformat + ".callgrind"
			self._logger.info("Saving callgrind data to %s" % file_name)
			func_stats = yappi.get_func_stats()
			func_stats.save(file_name, 'CALLGRIND')

			file_name = 'profiler-func-' + now__isoformat + ".pstats"
			self._logger.info("Saving (functions) pstats data to %s" % file_name)
			func_pstats = yappi.convert2pstats(yappi.get_func_stats())
			func_pstats.dump_stats(file_name)

			yappi.stop()
			yappi.clear_stats()

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			profiler=dict(
				displayName="Profiler Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="gdombiak",
				repo="OctoPrint-Profiler",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/gdombiak/OctoPrint-Profiler/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Profiler Plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
# __plugin_pythoncompat__ = ">=3,<4" # only python 3
# __plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = ProfilerPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
