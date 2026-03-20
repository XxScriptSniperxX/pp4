# coding: UTF-8

import os
from PySide6 import QtWidgets, QtCore, QtGui
import json
import amepyplot
from sysa.api.api import Session
from Utils.PluginPlotLib.graph_creator import GraphManager, GraphPage, SubGraph
from Utils.PluginGui.TreeTemplate import customTree as cTree
from Utils.PluginGui.resources.progress_bar import _default_callback_placeholder
from getpass import getuser
from datetime import datetime
from collections import defaultdict

try:
    from sysa.api.api import TableCriteria # from System Analyst 22.1
except ImportError:
    from AutomaticReportGeneration.ReportManager.TableCriteriaTemp import TableCriteria # before SAN 22.1


class ReportManager(object):
    """Object in charge of loading taskpad analysis content and maneuver template"""

    def __init__(self, templateReport, templateDir: str="", taskpads: list=None, tests: list=None):
        super().__init__()
        self.maneuver_Id = ''
        self.template_criteria_id_set = set()
        self.report_objects = dict()
        self.taskpad_analysis_names = []
        self.taskpad_analysis_criteria_values = dict()
        self.taskpad_analysis_spline_criteria_values = dict()
        self.taskpad_analysis_variables_values = dict()
        self.test_variables_values = dict()
        self.graph_manager = None

        # self.loadReportTemplate()
        self.report_backbone = templateReport
        self.sysaProject = Session().currentProject
        self.selected_taskpad = taskpads
        self.selected_tests = tests
        self.templateLocationDir = templateDir

    def loadManeuverTemplateExample(self, maneuver: str):
        '''
        Loads the json file containing details about the report associated to the computed taskpad in the SysA project.
        '''
        with open(maneuver, encoding='utf-8') as f:
            self.report_backbone = json.load(f)

    def getCriteriaIdFromBackbone(self):
        '''
        Concatenate the Id of each criteria needed for the report generation in a set.
        '''
        idSet = set()
        template = self.report_backbone
        for key in template.keys():
            page = template[key]
            for item in page["subgraphs"]:
                if "criteria_id_list" in item.keys():
                    for elem in item["criteria_id_list"]:
                        idSet.add(elem)
                elif "criteria_id_for_curve" in item.keys():
                    for elem in item["criteria_id_for_curve"]:
                        idSet.add(elem)
        self.template_criteria_id_set = idSet

    def loadProjectCriteria(self):
        """
        Loads for each taskpad the corresponding criterias and their values.
        Version compatible with new Gui - Siemens 2025/06
        """
        gatheredCriterias = defaultdict(lambda: defaultdict(dict))
        gatheredSplineCriterias = defaultdict(lambda: defaultdict(dict))
        taskpad_analysis_title = self.selected_taskpad[0]['maneuver']
        for taskpad in self.selected_taskpad:
            analysis_set = taskpad['taskpad_instance']
            td_name = taskpad['technical_definition']
            set_title = f"{td_name} - {taskpad_analysis_title}"
            for criteria in analysis_set.criteria:
                if criteria.isSpline:
                    try:
                        criteria.inputs
                    except AttributeError:
                        criteria = TableCriteria(criteria)
                    gatheredSplineCriterias[taskpad_analysis_title][set_title][criteria.id] = criteria
                else:
                    gatheredCriterias[taskpad_analysis_title][set_title][criteria.id] = criteria.value
        self.taskpad_analysis_criteria_values = gatheredCriterias
        self.taskpad_analysis_spline_criteria_values = gatheredSplineCriterias

    def loadProjectVariables(self, taskpads):
        """
        Loads Variables objects from taskpadAnalysis into a dict if the field variables_id_list is in report_backbone
        Modified by GC, Renault, Sce 68193, 24/01/24 (Old version still available named loadProjectVariablesOld)
        """
        hasVariableField = False
        for pages in self.report_backbone.values():
            for subgraph in pages["subgraphs"]:
                if "variables_id_list" in subgraph.keys():
                    hasVariableField = True
        if hasVariableField:
            self.taskpad_analysis_variables_values = {}
            project = self.sysaProject
            for taskpad in project.taskpadAnalysis:
                if (title := taskpad.title) in taskpads:
                    self.taskpad_analysis_variables_values[title] = {}
                    for study in taskpad.studies:
                        for run in study.runs:
                            run_title = run.title
                            var_list = run.variableResults()
                            self.taskpad_analysis_variables_values[title][run_title] = var_list

    def loadTestObjects(self):
        self.test_variables_values = {
            test['import_test']: {
                var['name']: {
                    'values': var['original_data'],
                    'gain': var['gain'],
                    'offset': var['offset']
                }
                for var in test['association_channels']
            }
            for test in self.selected_tests
        }

    def populateReportObjects(self, maneuver):
        """
        Instantiates the GraphManager that handles GraphPage setup.
        Modified by GC, Renault, Sce 68193, 24/01/24 (Old version still available named populateReportObjectsOld)
        """
        # assert len(taskpads) == 1  # to be modified to accept several ones...
        criterias = self.taskpad_analysis_criteria_values[maneuver]
        splines = self.taskpad_analysis_spline_criteria_values[maneuver]
        splines_tests = self.test_variables_values
        values = self.taskpad_analysis_variables_values
        template_dir = self.templateLocationDir
        self.graph_manager = GraphManager(self.report_backbone, taskpadCritValues=criterias,
                                          taskpadVarValues=values,
                                          taskpadSplineCritValues=splines,
                                          testsSplineCritValues=splines_tests,
                                          templateDir=template_dir)

    def getPlotWidgetFromTreeItemName(self, itemName: str, parentItemName: str):
        """
        Returns the PlotWidget of a GraphPage associated with the item named itemName
        :param itemName: name of the item selected
        :return: Returns the associated plotWidget if found, else None.
        """
        if parentItemName is None or parentItemName == "":
            for page, graphPage in self.graph_manager.graph_builder.items():
                if graphPage.title == itemName:
                    return graphPage.plot_widget
        else:
            for page, graphPage in self.graph_manager.graph_builder.items():
                if graphPage.title == parentItemName and any(
                        subgraph_title == itemName for subgraph_title in graphPage.sub_Graphs.keys()):
                    return graphPage.plot_widget
        return None

    def autoSetupReportObjects(self, plot_widgets_dict=None, callback=_default_callback_placeholder):
        """
        Loads criteria and variables from the SysA project. Then populates the GraphPages and subgraph according
        to the template layout. Plots all the graphs when all set.

        :param plot_widgets_dict: plotWidgets instantiated via MainWindow
        """
        callback(0, "Loading criterias from SysA Project ...")
        self.getCriteriaIdFromBackbone()
        callback(int((1 / 7) * 100), "Loading criterias from SysA Project ...")
        self.loadProjectCriteria()
        selected_maneuver = self.selected_taskpad[0]['maneuver']
        callback(int((2 / 7) * 100), "Loading variables from SysA Project ...")
        self.loadProjectVariables(selected_maneuver)
        if self.selected_tests:
            self.loadTestObjects()
        callback(int((3 / 7) * 100), "Populating report objects ...")
        self.populateReportObjects(selected_maneuver)
        callback(int((4 / 7) * 100), "Populating report objects ...")
        self.graph_manager.populateReportPages(plotWidgetDict=plot_widgets_dict)
        callback(int((5 / 7) * 100), "Populating report objects ...")
        self.graph_manager.populateReportSubgraphs()
        callback(int((6 / 7) * 100), "Populating report objects ...")
        self.graph_manager.setupSubgraphValuesForPlot()
        callback(int((7 / 7) * 100), "Ploting all graphs ...")
        self.graph_manager.plotAllSubgraphs(plot_style_taskpad=self.selected_taskpad,
                                            plot_style_test=self.selected_tests)


class DetailsPage(QtWidgets.QWidget):
    """
    Last page of the report with informations about the session and the user.
    """

    def __init__(self, maneuver_name=None, sysA_version=None, template_dir=None):
        super(DetailsPage, self).__init__()
        self.title = QtWidgets.QLabel("Informations sur le dépouillement")
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.maneuver = QtWidgets.QLabel("Manoeuvre : ")
        self.maneuver_name = QtWidgets.QLabel(f"{maneuver_name}")
        self.sysA_version = QtWidgets.QLabel("SysA version : ")
        self.sysA_version_text = QtWidgets.QLabel(f"{sysA_version}")
        self.mada_project = QtWidgets.QLabel("Projet courant : ")
        self.mada_project_label = QtWidgets.QLabel(f"{os.getcwd()}")
        self.user = QtWidgets.QLabel("Utilisateur (IPN) : ")
        self.user_label = QtWidgets.QLabel(f"{getuser()}")
        self.date = QtWidgets.QLabel("Date : ")
        self.date_value = QtWidgets.QLabel(str(datetime.today()).split(".")[0])
        self.template = QtWidgets.QLabel("Template : ")
        self.template_dir = QtWidgets.QLabel(f"{os.path.normpath(template_dir)}")

        global_grid_layout = QtWidgets.QGridLayout()
        global_grid_layout.addWidget(self.maneuver, 0, 0)
        global_grid_layout.addWidget(self.maneuver_name, 0, 1)
        global_grid_layout.addWidget(self.sysA_version, 1, 0)
        global_grid_layout.addWidget(self.sysA_version_text, 1, 1)
        global_grid_layout.addWidget(self.date, 2, 0)
        global_grid_layout.addWidget(self.date_value, 2, 1)
        global_grid_layout.addWidget(self.mada_project, 3, 0)
        global_grid_layout.addWidget(self.mada_project_label, 3, 1)
        global_grid_layout.addWidget(self.user, 4, 0)
        global_grid_layout.addWidget(self.user_label, 4, 1)
        global_grid_layout.addWidget(self.template, 5, 0)
        global_grid_layout.addWidget(self.template_dir, 5, 1)
        global_grid_layout.setColumnStretch(0, 0)
        global_grid_layout.setColumnStretch(1, 1)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.title)
        main_layout.addLayout(global_grid_layout, 33)
        main_layout.addStretch(100)

        self.setLayout(main_layout)

    def toPixmap(self, output_dir, filename_without_ext):
        """
        Function mocking the behavior of the amepyplot.plotWidget.toPixmap to add the last page to the report.

        :param output_dir: output directory path
        :param filename_without_ext: name of the final file without extension
        :return: String of the path where the image associated to the detail page is stored
        """
        file_output_path = os.path.join(output_dir, filename_without_ext + "details_page.png")
        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)
        pixmap.save(file_output_path, format="PNG")
        return file_output_path


if __name__ == '__main__':
    pass
