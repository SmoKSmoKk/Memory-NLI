"""
An NLI with Memory.
"""
from ctypes import alignment
from tkinter import CENTER
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import pyperclip

from argparse import Action

from IPython import get_ipython
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.core.interactiveshell import InteractiveShell

from idom import use_state

import os
import ast

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


import pandas as pd

from nl2pandas.backend.pandas_generator.context.context import Context
from nl2pandas.backend.pandas_generator.manager.manager import PandasManager
from nl2pandas.backend.pandas_generator.refiner.refiner import Refiner
from nl2pandas.backend.pandas_generator.code_generator.code_generator import CodeGenerator


shell = InteractiveShell()
context = Context(shell)
pandas_manager = PandasManager(context)


class MemoryNLI(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        This function gets the application into its initial state.
        """

        #variables for global storage
        global df
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/importable_dataframes/'
        file_path += "Kumpula-June-2016-w-metadata_clean_cl.txt"
        df = pd.read_csv(filepath_or_buffer=file_path)
        context.dataframes['df'] = {
            'columns': df.columns.tolist(),
            'indices': df.index.tolist()
        }
        context.active_dataframe = 'df'
        global action_info
        action_info = []
        global refiner
        refiner = Refiner(context)
        global past_utterances
        past_utterances = pd.DataFrame(columns = ["utterance", "action_info_index", "generation_utterance", "refined_kwargs", "dataframe"])
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/save_files/past_utterances_save.csv'
        if os.path.exists(file_path):
            past_utterances = pd.read_csv(filepath_or_buffer = file_path)
        global using_memory
        using_memory = False
        global unrefined
        unrefined = True

        main_box = toga.Box(style=Pack(direction=COLUMN))

        dataframe_input_label = toga.Label(
            "Name of the Datafrmae-File: ",
            style=Pack(padding=(0, 5))
        )
        self.dataframe_input = toga.TextInput(style=Pack(flex=1))

        dataframe_set_button = toga.Button(
            "Import Dataframe",
            on_press=lambda widget: self.import_dataframe(),
            style=Pack(padding=5)
        )

        dataframe_input_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
        dataframe_input_box.add(dataframe_input_label)
        dataframe_input_box.add(self.dataframe_input)
        dataframe_input_box.add(dataframe_set_button)

        utterance_input_label = toga.Label(
            "Write your utterance here: ",
            style=Pack(padding=(0, 5))
        )
        self.utterance_input = toga.TextInput(style=Pack(flex=1))

        utterance_input_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
        utterance_input_box.add(utterance_input_label)
        utterance_input_box.add(self.utterance_input)

        generate_nli_output_button = toga.Button(
            "Generate NLI Output",
            on_press=lambda widget: self.generate_pandas_nli_output(main_box),
            style=Pack(padding=5)
        )
        generate_rule_based_output_button = toga.Button(
            "Generate Rule Based Output",
            on_press=lambda widget: self.generate_rule_based_memory_output(main_box),
            style=Pack(padding=5)
        )
        generate_ai_based_output_button = toga.Button(
            "Generate AI Based Output",
            on_press=lambda widget: self.generate_ai_based_memory_output(main_box),
            style=Pack(padding=5)
        )
        self.generate_output_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.generate_output_box.add(generate_nli_output_button)
        self.generate_output_box.add(generate_rule_based_output_button)
        self.generate_output_box.add(generate_ai_based_output_button)

        main_box.add(dataframe_input_box)
        main_box.add(utterance_input_box)
        main_box.add(self.generate_output_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.on_exit = self.save_on_close
        self.main_window.show()

    def generate_ai_based_memory_output(self, main_box):
        '''
        This function genrates the AI memory output by using a sentence transformer to embed the user's utterance and
        the one from past_utterances and then compare them using cosine similarity. It only selects it as a match if
        the similarity clears a threshold.
        At the end it creates a dropdown menu so the user can see the functions and also a button to select the function.
        '''
        try:
            main_box.remove(self.function_selection_box)
        except:
            pass

        try:
            main_box.remove(self.unsure_text)
        except:
            pass

        try:
            main_box.remove(self.refine_box)
        except:
            pass

        try:
            main_box.remove(self.finalize_box)
        except:
            pass

        try:
            main_box.remove(self.refinement_options_box)
        except:
            pass

        global past_utterances
        global refiner
        global action_info
        global using_memory
        using_memory = True
        action_info = []
        options_df = pd.DataFrame(columns=["list_element", "probability", "utterance_index"])
        input_utterance = self.utterance_input.value

        model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        for utterance_index, past_utterance in past_utterances.iterrows():
            utterance = past_utterance['utterance']
            utterances = [utterance, input_utterance]
            embeddings = model.encode(utterances)
            similarity = cosine_similarity(embeddings[0].reshape(1,-1), embeddings[1].reshape(1,-1))[0][0]
            threshold = 0.5

            if similarity > threshold:
                temp_action_info = self.generate_action_info(past_utterances.iloc[utterance_index]['generation_utterance'])
                action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                similarity_percentage = round(similarity * 100, 2)
                action_info[-1]['probability'] = similarity_percentage
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{similarity_percentage:.2f}" + "%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": similarity_percentage, "utterance_index": utterance_index}])])

           
        options_df = options_df.sort_values(by=["probability"], ascending=False)

        action_info = sorted(action_info, key=lambda x: x['probability'], reverse=True)
        options_list = []
        for i in action_info:
            list_element = i['grounded_action'] + " (" + str(i["probability"]) + "%)"
            options_list.append(list_element)

        self.option_selection = toga.Selection(
                items = options_list,
                style=Pack(padding=5, flex = 1)
        )
        self.option_confirmation = toga.Button(
                "Select",
                on_press=lambda widget: self.show_selected_function(main_box, past_utterances_index=options_df.iloc[self.option_selection.items.index(self.option_selection.value)]["utterance_index"]),
                style=Pack(padding=5, width=100)
        )
        self.function_selection_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, alignment = CENTER))
        self.function_selection_box.add(self.option_selection)
        self.function_selection_box.add(self.option_confirmation)

        main_box.add(self.function_selection_box)


    def generate_rule_based_memory_output(self, main_box):
        '''
        This function generates the rule based output from memory. The rules are:
            - The user's utterance and the one from meomry are the same
            - The user's utterance is contained in the one from memory
            - The utterance from memory is contained in the user's utterance
        At the end it creates a dropdown menu so the user can see the functions and also a button to select the function.
        '''
        try:
            main_box.remove(self.function_selection_box)
        except:
            pass

        try:
            main_box.remove(self.unsure_text)
        except:
            pass

        try:
            main_box.remove(self.refine_box)
        except:
            pass

        try:
            main_box.remove(self.finalize_box)
        except:
            pass

        try:
            main_box.remove(self.refinement_options_box)
        except:
            pass

        global past_utterances
        global refiner
        global action_info
        global using_memory
        using_memory = True
        action_info = []
        options_df = pd.DataFrame(columns=["list_element", "probability", "utterance_index"])
        for utterance_index, past_utterance in past_utterances.iterrows():
            utterance = past_utterance['utterance']
            if utterance == self.utterance_input.value:
                temp_action_info = self.generate_action_info(past_utterances.iloc[utterance_index]['generation_utterance'])
                action_info.append(temp_action_info[past_utterances.iloc[utterance_index]['action_info_index']])
                action_info[-1]['probability'] = 100
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (100%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": 100, "utterance_index": utterance_index}])])
            #if the input is part of the utterance
            elif self.utterance_input.value in utterance:
                temp_action_info = self.generate_action_info(past_utterances.iloc[utterance_index]['generation_utterance'])
                action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                utterance_correspondence = round((len(self.utterance_input.value) / len(utterance)) * 100, 2)
                action_info[-1]['probability'] = utterance_correspondence
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])
            #if the utterance is part of the input
            elif utterance in self.utterance_input.value:
                temp_action_info = self.generate_action_info(past_utterances.iloc[utterance_index]['generation_utterance'])
                action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                utterance_correspondence = round((len(utterance) / len(self.utterance_input.value)) * 100, 2)
                action_info[-1]['probability'] = utterance_correspondence
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])

        options_df = options_df.sort_values(by=["probability"], ascending=False)

        action_info = sorted(action_info, key=lambda x: x['probability'], reverse=True)
        options_list = []
        for i in action_info:
            list_element = i['grounded_action'] + " (" + str(i["probability"]) + "%)"
            options_list.append(list_element)

        self.option_selection = toga.Selection(
                items = options_list,
                style=Pack(padding=5, flex = 1)
        )
        self.option_confirmation = toga.Button(
                "Select",
                on_press=lambda widget: self.show_selected_function(main_box, past_utterances_index=options_df.iloc[self.option_selection.items.index(self.option_selection.value)]["utterance_index"]),
                style=Pack(padding=5, width=100)
        )
        self.function_selection_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, alignment = CENTER))
        self.function_selection_box.add(self.option_selection)
        self.function_selection_box.add(self.option_confirmation)

        main_box.add(self.function_selection_box)

    def generate_pandas_nli_output(self, main_box):
        '''
        This function gets the NLI for Pandas output.
        At the end it creates a dropdown menu so the user can see the functions and also a button to select the function.
        '''
        try:
            main_box.remove(self.function_selection_box)
        except:
            pass

        try:
            main_box.remove(self.unsure_text)
        except:
            pass

        try:
            main_box.remove(self.refine_box)
        except:
            pass

        try:
            main_box.remove(self.finalize_box)
        except:
            pass

        try:
            main_box.remove(self.refinement_options_box)
        except:
            pass

        global using_memory
        using_memory = False
        global action_info
        action_info = self.generate_action_info(self.utterance_input.value)
        if action_info[0]['grounded_action'] == 'NOT_SURE':
            self.unsure_text = toga.Label(
                "No match found \n try somethin else",
                style=Pack(padding=(0, 5))
            )
            main_box.add(self.unsure_text)
        else:
            options_list = []
            for i in action_info:
                list_element = i['grounded_action'] + " (" + str(i["probability"]) + "%)"
                options_list.append(list_element)
            self.option_selection = toga.Selection(
                items = options_list,
                style=Pack(padding=5, flex = 1)
            )
            self.option_confirmation = toga.Button(
                "Select",
                on_press=lambda widget: self.show_selected_function(main_box),
                style=Pack(padding=5, width=100)
            )
            self.function_selection_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, alignment = CENTER))
            self.function_selection_box.add(self.option_selection)
            self.function_selection_box.add(self.option_confirmation)
            main_box.add(self.function_selection_box)

    def generate_action_info(self, line):
        action_info = pandas_manager.get_programs(line)
        return action_info

    def show_selected_function(self, main_box, past_utterances_index = None):
        '''
        This function shows the selected function in a read-only text box, generates a button for the user to go into the refinement view and
        generates two buttons to save the function into memory, one of them also copys it to the user's clipboard.
        '''
        try:
            main_box.remove(self.refine_box)
        except:
            pass

        try:
            main_box.remove(self.finalize_box)
        except:
            pass

        try:
            main_box.remove(self.refinement_options_box)
        except:
            pass

        global action_info
        global refiner
        global past_utterances
        global unrefined
        unrefined = True
        chosen_index = self.option_selection.items.index(self.option_selection.value)
        refiner = pandas_manager.get_refiner(action_info[chosen_index])
        if past_utterances_index is not None:
            refiner.refined_kwargs = ast.literal_eval(past_utterances["refined_kwargs"][past_utterances_index])
            refiner.update_df_dependencies()
            refiner.refine_kwargs()

        self.output_label = toga.Label(
            "Function: ",
            style=Pack(padding=(0, 5))
        )
        self.function_output = toga.TextInput(
            readonly = True,
            style=Pack(flex=1)
        )
        self.function_output.value = refiner.executable_function

        self.refine_button = toga.Button(
            "Refine",
            on_press=lambda widget: self.show_refinement_options(main_box),
            style=Pack(padding=5)
        )

        self.function_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
        self.function_box.add(self.output_label)
        self.function_box.add(self.function_output)
        self.function_box.add(self.refine_button)

        self.warning_label = toga.Label(
            text = '',
            style=Pack(padding=(0, 5), color = 'RED')
        )

        self.refine_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.refine_box.add(self.function_box)
        self.refine_box.add(self.warning_label)

        self.finalize_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, alignment = CENTER))
        self.finalize_button = toga.Button(
            "Finalize Output",
            on_press=lambda widget: self.finalize_output(past_utterances_index),
            style=Pack(padding=5)
        )
        self.finalize_and_copy_button = toga.Button(
            "Finalize and Copy Output",
            on_press=lambda widget: self.copy_to_clipboard(self.function_output.value, past_utterances_index),
            style=Pack(padding=5)
        )
        self.finalize_box.add(self.finalize_button)
        self.finalize_box.add(self.finalize_and_copy_button)

        main_box.add(self.refine_box)
        main_box.add(self.finalize_box)

    def show_refinement_options(self, main_box):
        '''
        This function shows all of the selected functions potential keyword arguments and 
        gives the user an appropriate element to set each of the keyword arguments.
        It also gives the user the option to save the refinement or to cancel it.
        '''
        try:
            main_box.remove(self.refinement_options_box)
        except:
            pass

        global refiner

        scope_options = refiner.get_scope_parameters()[1]
        additional_parameters = refiner.get_scope_parameters()[0]

        refinement_buttons_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
        scope_options_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        additional_parameters_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.refinement_options_box = toga.Box(style=Pack(direction=COLUMN, padding=5))

        refinement_save_button = toga.Button(
            "Save",
            on_press=lambda widget: self.save_refinement_options(main_box),
            style=Pack(padding=5)
        )

        refinement_cancel_button = toga.Button(
            "Cancel",
            on_press=lambda widget: self.cancel_refinement_options(main_box),
            style=Pack(padding=5)
        )

        scope_label = toga.Label(
            "Scope:",
            style=Pack(padding=(0, 5))
        )

        additional_parameters_label = toga.Label(
            "Additional Parameters: ",
            style=Pack(padding=(0, 5))
        )

        for key in scope_options:
            key_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
            key_label = toga.TextInput(
                readonly = True,
                style=Pack(padding=5)
            )
            key_label.value = key
            key_box.add(key_label)
            if scope_options[key]['selection'] == 'dropdown' or scope_options[key]['selection'] == 'dropdown_multi':
                dropdown_input = toga.Selection(
                    items = scope_options[key]['options'],
                    style=Pack(padding=5)
                )
                #catching what is probably a bug from nli for pandas or something it is using
                try:
                    dropdown_input.value = str(refiner._refined_kwargs[key])
                except:
                    pass
                key_box.add(dropdown_input)
            elif scope_options[key]['selection'] == 'text':
                text_input = toga.TextInput(style=Pack(padding=5))
                text_input.value = refiner._refined_kwargs[key]
                key_box.add(text_input)
            elif scope_options[key]['selection'] == 'number':
                number_input = toga.NumberInput(style=Pack(padding=5))
                number_input.value = refiner._refined_kwargs[key]
                key_box.add(number_input)
            scope_options_box.add(key_box)

        for key in additional_parameters:
            key_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment = CENTER))
            key_label = toga.TextInput(
                readonly = True,
                style=Pack(padding=5)
            )
            key_label.value = key
            key_box.add(key_label)
            if additional_parameters[key]['selection'] == 'dropdown' or additional_parameters[key]['selection'] == 'dropdown_multi':
                dropdown_input = toga.Selection(
                    items = additional_parameters[key]['options'],
                    style=Pack(padding=5)
                )
                #catching what is probably a bug from nli for pandas or something it is using
                try:
                    dropdown_input.value = str(refiner._refined_kwargs[key])
                except:
                    pass
                key_box.add(dropdown_input)
            elif additional_parameters[key]['selection'] == 'text':
                text_input = toga.TextInput(style=Pack(padding=5))
                text_input.value = refiner._refined_kwargs[key]
                key_box.add(text_input)
            elif additional_parameters[key]['selection'] == 'number':
                number_input = toga.NumberInput(style=Pack(padding=5))
                number_input.value = refiner._refined_kwargs[key]
                key_box.add(number_input)
            additional_parameters_box.add(key_box)

        refinement_buttons_box.add(refinement_save_button)
        refinement_buttons_box.add(refinement_cancel_button)

        self.refinement_options_box.add(refinement_buttons_box)
        self.refinement_options_box.add(scope_label)
        self.refinement_options_box.add(scope_options_box)
        self.refinement_options_box.add(additional_parameters_label)
        self.refinement_options_box.add(additional_parameters_box)

        main_box.remove(self.finalize_box)
        main_box.add(self.refinement_options_box)
        main_box.add(self.finalize_box)

    def cancel_refinement_options(self, main_box):
        main_box.remove(self.refinement_options_box)

    def save_refinement_options(self, main_box):
        '''
        This function creates a dictionary, that can be understood by the refiner class 
        and sets the refiner's kwargs variable to it.
        '''
        global unrefined
        unrefined = False
        new_refiner_kwargs = {}
        for key in range(len(self.refinement_options_box.children[2].children)):
            new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] = self.refinement_options_box.children[2].children[key].children[1].value
            if new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] == 'True':
                new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] = True
            elif new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] == 'False':
                new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] = False
            elif new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] == '':
                new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] = None
            elif new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] == 'None':
                new_refiner_kwargs[self.refinement_options_box.children[2].children[key].children[0].value] = None
        for key in range(len(self.refinement_options_box.children[4].children)):
            new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] = self.refinement_options_box.children[4].children[key].children[1].value
            if new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] == 'True':
                new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] = True
            elif new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] == 'False':
                new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] = False
            elif new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] == '':
                new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] = None
            elif new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] == 'None':
                new_refiner_kwargs[self.refinement_options_box.children[4].children[key].children[0].value] = None
        global refiner
        refiner.refined_kwargs = new_refiner_kwargs
        refiner.update_df_dependencies()
        refiner.refine_kwargs()
        self.function_output.value = refiner.executable_function
        main_box.remove(self.refinement_options_box)

    def finalize_output(self, past_utterances_index):
        '''
        This function creates the memory entry in the past_utterances dataframe, drops duplicates from it and 
        saves it with the save_on_close function.
        '''
        global action_info
        global refiner
        global df
        global past_utterances
        global using_memory
        if using_memory:
            chosen_action_info_index = past_utterances["action_info_index"][past_utterances_index]
            past_utterances = pd.concat([past_utterances, pd.DataFrame.from_records([{
                "utterance": action_info[0]['nl_utterance'],
                "action_info_index": chosen_action_info_index,
                "generation_utterance": action_info[self.option_selection.items.index(self.option_selection.value)]['nl_utterance'],
                "refined_kwargs": refiner._refined_kwargs,
                "dataframe": df
            }])])
        else:
            chosen_action_info_index = self.option_selection.items.index(self.option_selection.value)
            past_utterances = pd.concat([past_utterances, pd.DataFrame.from_records([{
                "utterance": action_info[0]['nl_utterance'],
                "action_info_index": chosen_action_info_index,
                "generation_utterance": action_info[0]['nl_utterance'],
                "refined_kwargs": refiner._refined_kwargs,
                "dataframe": df
            }])])
        past_utterances['refined_kwargs'] = past_utterances['refined_kwargs'].astype(str)
        past_utterances['dataframe'] = past_utterances['dataframe'].astype(str)
        past_utterances.drop_duplicates(keep='first', inplace=True)
        self.save_on_close()

    def copy_to_clipboard(self, text, past_utterances_index):
        '''
        This function calls the finalize_output function and after 
        copies the output function to the user's clipboard, using pyperclip.
        '''
        self.finalize_output(past_utterances_index)
        pyperclip.copy(text)

    def import_dataframe(self):
        '''
        This function imports the datafrmae from a file in the folder importable_dataframes and
        sets it as the active dataframe.
        '''
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/importable_dataframes/'
        file_path += self.dataframe_input.value
        global df
        df = pd.read_csv(filepath_or_buffer=file_path)
        context.dataframes['df'] = {
            'columns': df.columns.tolist(),
            'indices': df.index.tolist()
        }
        context.active_dataframe = 'df'

    def save_on_close(self):
        '''
        This function saves tha past_utterances dataframe into a csv file, so it can be loaded the next time the application is started.
        '''
        global past_utterances
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/save_files/past_utterances_save.csv'
        past_utterances.to_csv(file_path, index = False)


def main():
    return MemoryNLI()
