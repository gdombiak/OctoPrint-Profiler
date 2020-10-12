# coding=utf-8
from __future__ import absolute_import

import logging
from datetime import datetime

import octoprint.plugin
import yappi
from octoprint.events import Events


### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.


class ProfilerPlugin(octoprint.plugin.SettingsPlugin,
					 octoprint.plugin.AssetPlugin,
					 octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.StartupPlugin,
					 octoprint.plugin.EventHandlerPlugin):

	def __init__(self):
		super(ProfilerPlugin, self).__init__()
		self._logger = logging.getLogger("octoprint.plugins.profiler")

	# StartupPlugin mixin

	def on_after_startup(self):
		self._logger.info("Profiler loaded!")
		# Set logging level to what we have in the settings
		if self._settings.get_boolean(["debug_logging"]):
			self._logger.setLevel(logging.DEBUG)
		else:
			self._logger.setLevel(logging.INFO)

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			debug_logging=False,
			output_folder = '',
			profile_enabled=True,
			profile_scope='print_job',
			profile_clock_type='cpu'
		)

	def on_settings_save(self, data):
		old_debug_logging = self._settings.get_boolean(["debug_logging"])

		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		new_debug_logging = self._settings.get_boolean(["debug_logging"])
		if old_debug_logging != new_debug_logging:
			if new_debug_logging:
				self._logger.setLevel(logging.DEBUG)
			else:
				self._logger.setLevel(logging.INFO)

	def get_settings_version(self):
		return 1

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
			if self._profile_print_job():
				# Start Profiling
				self._logger.info("Profiling started")
				yappi.start()
		if event == Events.PRINT_DONE or event == Events.PRINT_CANCELLED:
			if self._profile_print_job():
				# Stop profiling and save statistics to a file for later analysis
				now__isoformat = datetime.now().isoformat()

				file_name = self._profile_output_folder() + 'profiler-func-' + now__isoformat + ".callgrind"
				self._logger.info("Saving callgrind data to %s" % file_name)
				func_stats = yappi.get_func_stats()
				func_stats.save(file_name, 'CALLGRIND')

				file_name = self._profile_output_folder() + 'profiler-func-' + now__isoformat + ".pstats"
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

	##~~ Private functions

	def _profile_print_job(self):
		"""Returns true if profiler will start profiling when a print job starts and stops profiling
		when print job finished (successfully or not)
		:return: True if profiling is enabled and we need to profile while printing
		"""
		return self._settings.get_boolean(["profile_enabled"]) and self._settings.get(["profile_scope"]) == 'print_job'

	def _profile_output_folder(self):
		"""
		Returns folder where profiling results will be saved
		:return: Path where pstats and callgrind files will be saved
		"""
		return self._settings.get(["output_folder"])


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
