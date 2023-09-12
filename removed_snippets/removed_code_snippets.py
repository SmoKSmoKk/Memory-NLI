            '''
            elif len(self.utterance_input.value) < len(utterance):
                #if the input is a prefix to the utterance
                if utterance[0:len(self.utterance_input.value)] == self.utterance_input.value:
                    temp_action_info = self.generate_action_info(utterance)
                    action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                    utterance_correspondence = (len(self.utterance_input.value) / len(utterance)) * 100
                    list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                    options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])
                #íf the input is a suffix to the utterance
                elif utterance[-len(self.utterance_input.value)] == self.utterance_input.value:
                    temp_action_info = self.generate_action_info(utterance)
                    action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                    utterance_correspondence = (len(self.utterance_input.value) / len(utterance)) * 100
                    list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                    options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])
            #if the utterance is a prefix to the input
            elif utterance == self.utterance_input.value[0:len(utterance)]:
                temp_action_info = self.generate_action_info(utterance)
                action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                utterance_correspondence = (len(utterance) / len(self.utterance_input.value)) * 100
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])
            #if the utterance is a suffix to the input
            elif utterance == self.utterance_input.value[-len(utterance)]:
                temp_action_info = self.generate_action_info(utterance)
                action_info.append(temp_action_info[past_utterances['action_info_index'][utterance_index]])
                utterance_correspondence = (len(utterance) / len(self.utterance_input.value)) * 100
                list_element = temp_action_info[past_utterances['action_info_index'][utterance_index]]['grounded_action'] + " (" + f"{utterance_correspondence:.2f}" + "%)"
                options_df = pd.concat([options_df, pd.DataFrame.from_records([{"list_element": list_element, "probability": utterance_correspondence, "utterance_index": utterance_index}])])
            '''