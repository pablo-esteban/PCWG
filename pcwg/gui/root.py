# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 14:41:26 2016

@author: Stuart
"""

import sys
import os
import os.path
import datetime
import traceback

import Tkinter as tk
import tkFileDialog
import tkMessageBox

from ..update import update
from ..core import analysis as core_analysis
from ..core import share
from ..core import benchmark

from ..configuration.preferences_configuration import Preferences
from ..configuration.benchmark_configuration import BenchmarkConfiguration
from ..configuration.analysis_configuration import AnalysisConfiguration
from ..configuration.portfolio_configuration import PortfolioConfiguration

from ..exceptions.handling import ExceptionHandler
from ..core.status import Status

import version as ver

import base_dialog
import analysis
import portfolio


class ExportDataSetDialog(base_dialog.BaseDialog):

    def __init__(self, master):

        self.cleanDataset = True
        self.allDatasets = False
        self.calibrationDatasets = False
        base_dialog.BaseDialog.__init__(self, master)

    def validate(self):

        valid = any(self.getSelections())

        if valid:
            return 1
        else:
            return 0

    def body(self, master):

        spacer = tk.Label(master, text=" " * 30)

        spacer.grid(row=self.row,
                    column=self.titleColumn,
                    columnspan=2)

        spacer = tk.Label(master, text=" " * 30)

        spacer.grid(row=self.row,
                    column=self.secondButtonColumn, columnspan=2)

        self.row += 1

        cleanDataset = self.cleanDataset
        allDatasets = self.allDatasets
        calibrationDatasets = self.calibrationDatasets

        self.cleanDataset = self.addCheckBox(master,
                                             "Clean Combined Dataset:",
                                             cleanDataset)

        spacer = tk.Label(master, text="Extra Time Series:")

        spacer.grid(row=self.row,
                    column=self.titleColumn,
                    columnspan=2)

        self.row += 1

        self.allDatasets = self.addCheckBox(master,
                                            "    Filtered Individual Datasets:",
                                            allDatasets)

        self.calibrationDatasets = self.addCheckBox(master,
                                                    "    Calibration Datasets:",
                                                    calibrationDatasets)

    def getSelections(self):

        return (bool(self.cleanDataset.get()),
                bool(self.allDatasets.get()),
                bool(self.calibrationDatasets.get()))

    def apply(self):

        return self.getSelections()

        
class UserInterface:

    def __init__(self, preferences):

        ExceptionHandler.initialize_handler(self.add_exception)
        Status.initialize_status(self.add_message, preferences.verbosity)

        self.analysis = None
        self.analysisConfiguration = None

        self.root = tk.Tk()
        self.root.geometry("860x400")
        self.root.title("PCWG")
        
        try:
            self.root.iconbitmap(os.path.join("Resources", "logo.ico"))
        except:
            Status.add("Can't set icon")
            
        self.verbosity = Preferences.get().verbosity

        consoleframe = tk.Frame(self.root)
        commandframe = tk.Frame(self.root)

        # analyse
        analyse_group = tk.LabelFrame(commandframe,
                                      text="Analysis",
                                      padx=5,
                                      pady=5)

        analyse_group_top = tk.Frame(analyse_group)
        analyse_group_bottom = tk.Frame(analyse_group)

        load_button = tk.Button(analyse_group_bottom,
                                text="Load",
                                command=self.LoadAnalysis)

        edit_button = tk.Button(analyse_group_bottom,
                                text="Edit",
                                command=self.EditAnalysis)

        new_button = tk.Button(analyse_group_bottom,
                               text="New",
                               command=self.NewAnalysis)

        calculate_button = tk.Button(analyse_group_top,
                                     text="Calculate",
                                     command=self.Calculate)

        export_report_button = tk.Button(analyse_group_top,
                                         text="Export Report",
                                         command=self.ExportReport)

        export_time_series_button = tk.Button(analyse_group_top,
                                              text="Export Time Series",
                                              command=self.ExportTimeSeries)

        export_training_data_button = tk.Button(analyse_group_top,
                                              text="Export Training Data",
                                              command=self.ExportTrainingData)

        export_pdm_button = tk.Button(analyse_group_top,
                                              text="Export PDM",
                                              command=self.ExportPDM)

        load_button.pack(side=tk.RIGHT, padx=5, pady=5)
        edit_button.pack(side=tk.RIGHT, padx=5, pady=5)
        new_button.pack(side=tk.RIGHT, padx=5, pady=5)
        calculate_button.pack(side=tk.LEFT, padx=5, pady=5)
        export_report_button.pack(side=tk.LEFT, padx=5, pady=5)
        export_time_series_button.pack(side=tk.LEFT, padx=5, pady=5)
        export_training_data_button.pack(side=tk.LEFT, padx=5, pady=5)
        export_pdm_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.analysisFilePathLabel = tk.Label(analyse_group_bottom,
                                              text="Analysis File")

        self.analysisFilePathTextBox = tk.Entry(analyse_group_bottom)
        self.analysisFilePathTextBox.config(state=tk.DISABLED)

        self.analysisFilePathLabel.pack(side=tk.LEFT,
                                        anchor=tk.NW,
                                        padx=5,
                                        pady=5)

        self.analysisFilePathTextBox.pack(side=tk.RIGHT,
                                          anchor=tk.NW,
                                          fill=tk.X,
                                          expand=1,
                                          padx=5,
                                          pady=5)

        analyse_group_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        analyse_group_top.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        analyse_group.pack(side=tk.TOP,
                           padx=10,
                           pady=5,
                           anchor=tk.NW,
                           fill=tk.X,
                           expand=1)

        # portfolio
        portfolio_group = tk.LabelFrame(commandframe,
                                        text="PCWG-Share-X",
                                        padx=5,
                                        pady=5)

        portfolio_group_top = tk.Frame(portfolio_group)
        portfolio_group_bottom = tk.Frame(portfolio_group)

        run_portfolio_button = tk.Button(portfolio_group_top,
                                         text="PCWG-Share-1.0",
                                         command=self.PCWG_Share_1_Portfolio)

        run_portfolio_button.pack(side=tk.LEFT, padx=5, pady=5)

        run_portfolio_button = tk.Button(portfolio_group_top,
                                         text="PCWG-Share-1.1",
                                         command=self.PCWG_Share_1_dot_1_Portfolio)

        run_portfolio_button.pack(side=tk.LEFT, padx=5, pady=5)

        load_portfolio_button = tk.Button(portfolio_group_bottom,
                                          text="Load",
                                          command=self.load_portfolio)

        edit_portfolio_button = tk.Button(portfolio_group_bottom,
                                          text="Edit",
                                          command=self.edit_portfolio)

        new_portfolio_button = tk.Button(portfolio_group_bottom,
                                         text="New",
                                         command=self.new_portfolio)

        load_portfolio_button.pack(side=tk.RIGHT, padx=5, pady=5)
        edit_portfolio_button.pack(side=tk.RIGHT, padx=5, pady=5)
        new_portfolio_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.portfolioFilePathLabel = tk.Label(portfolio_group_bottom,
                                               text="Portfolio File")

        self.portfolioFilePathTextBox = tk.Entry(portfolio_group_bottom)
        self.portfolioFilePathTextBox.config(state=tk.DISABLED)

        self.portfolioFilePathLabel.pack(side=tk.LEFT,
                                         anchor=tk.NW,
                                         padx=5,
                                         pady=5)

        self.portfolioFilePathTextBox.pack(side=tk.RIGHT,
                                           anchor=tk.NW,
                                           fill=tk.X,
                                           expand=1,
                                           padx=5,
                                           pady=5)

        portfolio_group_bottom.pack(side=tk.BOTTOM,
                                    fill=tk.BOTH,
                                    expand=1)

        portfolio_group_top.pack(side=tk.TOP,
                                 fill=tk.BOTH,
                                 expand=1)

        portfolio_group.pack(side=tk.LEFT,
                             padx=10,
                             pady=5,
                             fill=tk.X,
                             expand=1)

        # misc
        misc_group = tk.LabelFrame(commandframe,
                                   text="Miscellaneous",
                                   padx=5,
                                   pady=5)

        misc_group_top = tk.Frame(misc_group)
        msic_group_bottom = tk.Frame(misc_group)

        benchmark_button = tk.Button(misc_group_top,
                                     text="Benchmark",
                                     command=self.RunBenchmark)

        clear_console_button = tk.Button(misc_group_top,
                                         text="Clear Console",
                                         command=self.ClearConsole)

        about_button = tk.Button(msic_group_bottom,
                                 text="About",
                                 command=self.About)

        benchmark_button.pack(side=tk.LEFT, padx=5, pady=5)
        clear_console_button.pack(side=tk.LEFT, padx=5, pady=5)
        about_button.pack(side=tk.LEFT, padx=5, pady=5)

        msic_group_bottom.pack(side=tk.BOTTOM)
        misc_group_top.pack(side=tk.TOP)

        misc_group.pack(side=tk.RIGHT, padx=10, pady=5)

        # console
        scrollbar = tk.Scrollbar(consoleframe,
                                 orient=tk.VERTICAL)

        self.listbox = tk.Listbox(consoleframe,
                                  yscrollcommand=scrollbar.set,
                                  selectmode=tk.EXTENDED)

        scrollbar.configure(command=self.listbox.yview)

        self.listbox.grid(column=0, row=0, sticky='nsew')
        scrollbar.grid(column=1, row=0, sticky='ns')

        consoleframe.grid_columnconfigure(0, weight=1)
        consoleframe.grid_columnconfigure(1, weight=0)
        consoleframe.grid_rowconfigure(0, weight=1)

        commandframe.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        consoleframe.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        preferences = Preferences.get()

        if len(preferences.analysisLastOpened) > 0:
            try:
                Status.add("Loading last analysis opened")
                self.LoadAnalysisFromPath(preferences.analysisLastOpened)
            except IOError:
                Status.add("Couldn't load last analysis: File could not be found.")
            except ExceptionHandler.ExceptionType as e:
                ExceptionHandler.add(e, "Couldn't load last analysis")
                    
        if len(preferences.portfolioLastOpened) > 0 and os.path.isfile(preferences.portfolioLastOpened):
            try:
                Status.add("Loading last portfolio opened")
                self.LoadPortfolioFromPath(preferences.portfolioLastOpened)
            except IOError:
                Status.add("Couldn't load last portfolio: File could not be found.")
            except ExceptionHandler.ExceptionType as e:
                ExceptionHandler.add(e, "Couldn't load last portfolio")
                    
        self.update()
        self.root.mainloop()

    def update(self):

        updator = update.Updator()

        if updator.is_update_available:

            if tkMessageBox.askyesno("New Version Available",
                                     "A new version is available (current version {0}), do you want to upgrade to {1} (restart required)?".format(updator.current_version, updator.latest_version)):

                try:
                    updator.download_latest_version()
                except ExceptionHandler.ExceptionType as e:

                    Status.add("Failed to download latest version: {0}".format(e), red=True)
                    return

                try:
                    updator.start_extractor()
                except ExceptionHandler.ExceptionType as e:

                    Status.add("Cannot start extractor: {0}".format(e), red=True)
                    return

                Status.add("Exiting")
                sys.exit(0)

        else:

            Status.add("No updates available")

    def RunBenchmark(self):

        preferences = Preferences.get()

        self.LoadAnalysisFromPath("")

        self.ClearConsole()

        # read the benchmark config xml
        path = tkFileDialog.askopenfilename(parent=self.root,
                                            title="Select Benchmark Configuration",
                                            initialdir=preferences.benchmark_last_opened_dir(),
                                            initialfile=preferences.benchmark_last_opened_file())

        if len(path) > 0:

            try:
                preferences.benchmarkLastOpened = path
                preferences.save()
            except ExceptionHandler.ExceptionType as e:
                ExceptionHandler.add(e, "Cannot save preferences")

            Status.add("Loading benchmark configuration file: %s" % path)
            benchmarkConfig = BenchmarkConfiguration(path)

            Status.add("Loaded benchmark configuration: %s" % benchmarkConfig.name)
            Status.add("")

            benchmarkPassed = True
            totalTime = 0.0

            for i in range(len(benchmarkConfig.benchmarks)):
                benchmark = benchmarkConfig.benchmarks[i]
                Status.add("Executing Benchmark %d of %d" % (i + 1, len(benchmarkConfig.benchmarks)))
                benchmarkResults = self.BenchmarkAnalysis(benchmark.absolute_path,  benchmarkConfig.tolerance, benchmark.base_line_mode, benchmark.expectedResults)
                benchmarkPassed = benchmarkPassed & benchmarkResults[0]
                totalTime += benchmarkResults[1]

            if benchmarkPassed:
                Status.add("All benchmarks passed")
            else:
                Status.add("There are failing benchmarks", red=True)

            Status.add("Total Time Taken: %fs" % totalTime)

        else:

            Status.add("No benchmark loaded", red=True)

    def BenchmarkAnalysis(self, path, tolerance, base_line_mode, dictExpectedResults):

            Status.add("Calculating %s (please wait)..." % path)

            Status.add("Benchmark Tolerance: %s" % self.formatPercentTwoDP(tolerance))

            benchmarkPassed = True
            start = datetime.datetime.now()

            try:

                analysis = benchmark.BenchmarkAnalysis(AnalysisConfiguration(path), base_line_mode)

            except ExceptionHandler.ExceptionType as e:

                analysis = None
                Status.add("ERROR: {0}".format(e))
                benchmarkPassed = False

            if analysis is not None:

                for (field, value) in dictExpectedResults.iteritems():

                    try:
                        benchmarkPassed = benchmarkPassed & self.compareBenchmark(field, value, float(eval("analysis.%s" % field)), tolerance)
                    except Exception as e:
                        raise Exception("Evaluation of analysis.{f} has failed, does this property exist? {e}".format(f=field, e=e))

            if benchmarkPassed:
                Status.add("Benchmark Passed")
            else:
                Status.add("Benchmark Failed", red=True)

            end = datetime.datetime.now()

            timeTaken = (end - start).total_seconds()
            Status.add("Time Taken: %fs" % timeTaken)

            Status.add("")

            return (benchmarkPassed, timeTaken)

    def formatPercentTwoDP(self, value):
        return "%0.2f%%" % (value * 100.0)

    def compareBenchmark(self, title, expected, actual, tolerance):

        diff = abs(expected - actual)
        passed = (diff <= tolerance)

        text = "{title}: {expec:0.10} (expected) vs {act:0.10} (actual) =>".format(title=title, expec=expected, act=actual)

        if passed:
            Status.add("%s passed" % text)
        else:
            Status.add("%s failed" % text, red=True)

        return passed

    def EditAnalysis(self):

        if self.analysisConfiguration is None:
            Status.add("ERROR: Analysis not loaded", red=True)
            return

        analysis.AnalysisConfigurationDialog(self.root,
                                             self.LoadAnalysisFromPath,
                                             self.analysisConfiguration)

    def NewAnalysis(self):

        conf = AnalysisConfiguration()
        analysis.AnalysisConfigurationDialog(self.root,
                                             self.LoadAnalysisFromPath, conf)

    def LoadAnalysis(self):

        preferences = Preferences.get()
        fileName = tkFileDialog.askopenfilename(parent=self.root,
                                                initialdir=preferences.analysis_last_opened_dir(),
                                                defaultextension=".xml")

        if len(fileName) < 1:
            return

        self.LoadAnalysisFromPath(fileName)

    def LoadAnalysisFromPath(self, fileName):

            try:
                preferences = Preferences.get()
                preferences.analysisLastOpened = fileName
                preferences.save()
            except ExceptionHandler.ExceptionType as e:
                ExceptionHandler.add(e, "Cannot save preferences")

            self.analysisFilePathTextBox.config(state=tk.NORMAL)
            self.analysisFilePathTextBox.delete(0, tk.END)
            self.analysisFilePathTextBox.insert(0, fileName)
            self.analysisFilePathTextBox.config(state=tk.DISABLED)

            self.analysis = None
            self.analysisConfiguration = None

            if len(fileName) > 0:

                try:
                    self.analysisConfiguration = AnalysisConfiguration(fileName)
                    Status.add("Analysis config loaded: %s" % fileName)
                except ExceptionHandler.ExceptionType as e:

                    ExceptionHandler.add(e, "ERROR loading config")

    def LoadPortfolioFromPath(self, fileName):

            try:
                preferences = Preferences.get()
                preferences.portfolioLastOpened = fileName
                preferences.save()
            except ExceptionHandler.ExceptionType as e:
                ExceptionHandler.add(e, "Cannot save preferences")

            self.portfolioFilePathTextBox.config(state=tk.NORMAL)
            self.portfolioFilePathTextBox.delete(0, tk.END)
            self.portfolioFilePathTextBox.insert(0, fileName)
            self.portfolioFilePathTextBox.config(state=tk.DISABLED)

            self.portfolioConfiguration = None

            if len(fileName) > 0 and os.path.isfile(fileName):

                try:
                    self.portfolioConfiguration = PortfolioConfiguration(fileName)
                    Status.add("Portfolio config loaded: %s" % fileName)
                except ExceptionHandler.ExceptionType as e:

                    ExceptionHandler.add(e, "ERROR loading config")

    def ExportReport(self):

            preferences = Preferences.get()

            if self.analysis is None:
                Status.add("ERROR: Analysis not yet calculated", red=True)
                return


            try:

                fileName = tkFileDialog.asksaveasfilename(parent=self.root,
                                                          defaultextension=".xls",
                                                          initialfile="report.xls",
                                                          title="Save Report",
                                                          initialdir=preferences.analysis_last_opened_dir())

                self.analysis.report(fileName)
                Status.add("Report written to %s" % fileName)

            except ExceptionHandler.ExceptionType as e:

                ExceptionHandler.add(e, "ERROR Exporting Report")

    def ExportPDM(self):

            preferences = Preferences.get()

            if self.analysis is None:
                Status.add("ERROR: Analysis not yet calculated", red=True)
                return

            if not hasattr(self.analysis, 'hubPowerDeviations'):
                Status.add("ERROR: PDM not calculated", red=True)
                return

            try:

                fileName = tkFileDialog.asksaveasfilename(parent=self.root,
                                                          defaultextension=".xml",
                                                          initialfile="power_deviation_matrix.xml",
                                                          title="Save Report",
                                                          initialdir=preferences.analysis_last_opened_dir())

                self.analysis.report_pdm(fileName)
                Status.add("Power Deviation Matrix written to %s" % fileName)

            except ExceptionHandler.ExceptionType as e:

                ExceptionHandler.add(e, "ERROR Exporting Report")

    def PCWG_Share_1_Portfolio(self):

        if self.portfolioConfiguration is None:
            Status.add("ERROR: Portfolio not loaded", red=True)
            return

        try:

            share.PcwgShare01Portfolio(self.portfolioConfiguration)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e)

    def PCWG_Share_1_dot_1_Portfolio(self):

        if self.portfolioConfiguration is None:
            Status.add("ERROR: Portfolio not loaded", red=True)
            return

        try:

            share.PcwgShare01dot1Portfolio(self.portfolioConfiguration)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e)
        
    def new_portfolio(self):

        try:

            portfolioConfiguration = PortfolioConfiguration()
            portfolio.PortfolioDialog(self.root,
                                      self.LoadPortfolioFromPath,
                                      portfolioConfiguration)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e)

    def edit_portfolio(self):

        if self.portfolioConfiguration is None:
            Status.add("ERROR: Portfolio not loaded", red=True)
            return

        try:

            portfolio.PortfolioDialog(self.root,
                                      self.LoadPortfolioFromPath,
                                      self.portfolioConfiguration)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e)

    def load_portfolio(self):

        try:

            preferences = Preferences.get()
            initial_dir = preferences.portfolio_last_opened_dir()
            initial_file = preferences.portfolio_last_opened_file()

            # read the benchmark config xml
            portfolio_path = tkFileDialog.askopenfilename(parent=self.root,
                                                          title="Select Portfolio Configuration",
                                                          initialfile=initial_file,
                                                          initialdir=initial_dir)

            self.LoadPortfolioFromPath(portfolio_path)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e)

    def ExportTimeSeries(self):

        if self.analysis is None:
            Status.add("ERROR: Analysis not yet calculated", red=True)
            return

        try:

            preferences = Preferences.get()
            selections = ExportDataSetDialog(self.root)
            clean, full, calibration = selections.getSelections()

            fileName = tkFileDialog.asksaveasfilename(parent=self.root,
                                                      defaultextension=".csv",
                                                      initialfile="timeseries.csv",
                                                      title="Save Time Series",
                                                      initialdir=preferences.analysis_last_opened_dir())

            self.analysis.export_time_series(fileName, clean, full, calibration)

            if clean:
                    Status.add("Time series written to %s" % fileName)

            if any((full, calibration)):
                    Status.add("Extra time series have been written to %s" % self.analysis.config.path.split(".")[0] + "_TimeSeriesData")

        except ExceptionHandler.ExceptionType as e:
            ExceptionHandler.add(e, "ERROR Exporting Time Series")

    def ExportTrainingData(self):

        if self.analysis is None:
            Status.add("ERROR: Analysis not yet calculated", red=True)
            return

        try:

            preferences = Preferences.get()

            fileName = tkFileDialog.asksaveasfilename(parent=self.root,
                                                      defaultextension=".csv",
                                                      initialfile="training_data.csv",
                                                      title="Save Training Data",
                                                      initialdir=preferences.analysis_last_opened_dir())

            self.analysis.export_training_data(fileName)

            Status.add("Time series written to %s" % fileName)

        except ExceptionHandler.ExceptionType as e:
            ExceptionHandler.add(e, "ERROR Exporting Time Series")

    def Calculate(self):

        if self.analysisConfiguration is None:
            Status.add("ERROR: Analysis Config file not specified", red=True)
            return

        try:

            self.analysis = core_analysis.Analysis(self.analysisConfiguration)

        except ExceptionHandler.ExceptionType as e:

            ExceptionHandler.add(e, "ERROR Calculating Analysis")

    def ClearConsole(self):
        self.listbox.delete(0, tk.END)
        self.root.update()

    def About(self):

        tkMessageBox.showinfo("PCWG-Tool About", "Version: {vers} \nVisit http://www.pcwg.org for more info".format(vers=ver.version))

    def add_message(self, message, red=False, verbosity=1):

        try:

            self.listbox.insert(tk.END, message)

            if red:
                self.listbox.itemconfig(tk.END, {'bg': 'red', 'foreground': 'white'})

            self.listbox.see(tk.END)
            self.root.update()

        except:

            print "Can't write message: {0}".format(message)

    def add_exception(self, exception, custom_message=None):

        try:

            if custom_message is not None:
                message = "{0}: {1}".format(custom_message, exception)
            else:
                message = "{0}".format(exception)

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            # write full traceback
            tb = traceback.extract_tb(exc_tb)
            tb_list = traceback.format_list(tb)

            for line in tb_list:
                self.add_message(line, red=True)

            self.add_message("Exception Type {0} in {1} line {2}.".format(exc_type.__name__, fname, exc_tb.tb_lineno), red=True)
            self.add_message(message, red=True)

        except:

            self.add_message("Can't write exception")
