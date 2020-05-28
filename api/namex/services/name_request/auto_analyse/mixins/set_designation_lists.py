from namex.constants import \
    BCProtectedNameEntityTypes, BCUnprotectedNameEntityTypes, XproUnprotectedNameEntityTypes, \
    DesignationPositionCodes, LanguageCodes

from namex.utils.common import parse_dict_of_lists


class SetDesignationsListsMixin(object):
    def _set_designations(self):
        # Set available designations for entity type selected by user (by default designations related to 'CR' entity type)
        # _designation_any_list_user and _designation_end_list_user contain the only correct designations
        self._set_designations_by_entity_type_user()

        # Set _designation_any_list and _designation_end_list based on company name typed by user
        # Set _all_designations (general list) based on company name typed by user
        # All previous set designations have correct position, but may belong to wrong entity type
        self._set_designations_by_input_name()

        # Set _misplaced_designation_end_list which contains <end> designations in other part of the name
        self._set_designations_incorrect_position_by_input_name()

        # Set _entity_type_any_designation for designations found on company name typed by user
        self._set_entity_type_any_designation()

        # Set _entity_type_end_designation for designations found on company name typed by user
        self._set_entity_type_end_designation()

        # Set _misplaced_designation_all based on company name typed by user
        # self._set_misplaced_designation_in_input_name()

        # Set all designations based on entity type typed by user,'CR' by default
        self._all_designations_user = self._eng_designation_all_list_correct + self._fr_designation_all_list_correct

        # self._all_designations_user_no_periods = remove_periods_designation(self._all_designations_user)
        # self._all_designations_user_no_periods.sort(key=len, reverse=True)

    '''
    Set the corresponding entity type for designations <any> found in name
    '''

    def _set_entity_type_any_designation(self):
        syn_svc = self.synonym_service
        designation_any_list = self._designation_any_list

        all_any_designations = syn_svc.get_all_any_designations().data

        self._entity_type_any_designation = syn_svc.get_entity_type_any_designation(
            entity_any_designation_dict=parse_dict_of_lists(all_any_designations),
            all_designation_any_end_list=designation_any_list
        ).data

    '''
    Set the corresponding entity type for designations <end> found in name
    '''

    def _set_entity_type_end_designation(self):
        syn_svc = self.synonym_service
        # entity_end_designation_dict = self._entity_end_designation_dict
        designation_end_list = self._designation_end_list

        all_end_designations = syn_svc.get_all_end_designations().data

        self._entity_type_end_designation = syn_svc.get_entity_type_end_designation(
            entity_end_designation_dict=parse_dict_of_lists(all_end_designations),
            all_designation_any_end_list=designation_end_list
        ).data

    def _set_designations_by_entity_type_user(self):
        syn_svc = self.synonym_service
        entity_type = self.entity_type

        entity_type_code = None
        if BCProtectedNameEntityTypes(entity_type):
            entity_type_code = BCProtectedNameEntityTypes(entity_type)
        elif BCUnprotectedNameEntityTypes(entity_type):
            entity_type_code = BCUnprotectedNameEntityTypes(entity_type)
        elif XproUnprotectedNameEntityTypes(entity_type):
            entity_type_code = XproUnprotectedNameEntityTypes(entity_type)

        self._eng_designation_any_list_correct = syn_svc.get_designations(entity_type_code=entity_type_code.value,
                                                                          position_code=DesignationPositionCodes.ANY.value,
                                                                          lang=LanguageCodes.ENG.value).data

        self._eng_designation_end_list_correct = syn_svc.get_designations(entity_type_code=entity_type_code.value,
                                                                          position_code=DesignationPositionCodes.END.value,
                                                                          lang=LanguageCodes.ENG.value).data

        self._fr_designation_any_list_correct = syn_svc.get_designations(entity_type_code=entity_type_code.value,
                                                                         position_code=DesignationPositionCodes.ANY.value,
                                                                         lang=LanguageCodes.FR.value).data

        self._fr_designation_end_list_correct = syn_svc.get_designations(entity_type_code=entity_type_code.value,
                                                                         position_code=DesignationPositionCodes.END.value,
                                                                         lang=LanguageCodes.FR.value).data

        self._eng_designation_all_list_correct = self._eng_designation_any_list_correct + self._eng_designation_end_list_correct
        self._eng_designation_all_list_correct.sort(key=len, reverse=True)

        self._fr_designation_all_list_correct = self._fr_designation_any_list_correct + self._fr_designation_end_list_correct
        self._fr_designation_all_list_correct.sort(key=len, reverse=True)

        self._designation_any_list_correct = self._eng_designation_any_list_correct + self._fr_designation_any_list_correct
        self._designation_any_list_correct.sort(key=len, reverse=True)

        self._designation_end_list_correct = self._eng_designation_end_list_correct + self._fr_designation_end_list_correct
        self._designation_end_list_correct.sort(key=len, reverse=True)

    '''
    Set designations in <any> and <end> positions regardless the entity type. 
    designation_any_list: Retrieves all designations properly placed anywhere in the name regardless the entity type.
                           <Entity type>-Valid English Designations_any Stop
                           English Designations_any Stop.
    designation_end_list: Retrieves all designations properly placed at the end in the name regardless the entity type
                           <Entity type>-Valid English Designations_end Stop
                           English Designations_end Stop.
   all_designations: Retrieves misplaced and correctly placed designations.
     Note: The previous lists contain designations that are in the correct position. For instance, designations with <end> position
           found anywhere are not counted here, they are counted in _set_designations_incorrect_position_by_input_name.
    '''

    def _set_designations_by_input_name(self):
        syn_svc = self.synonym_service
        np_svc = self.name_processing_service

        # original_name = self.get_original_name()
        # Get the first section of name when exists slash. For instance, ARMSTRONG PLUMBING LTD./ ARMSTRONG PLUMBING LIMITEE
        # Just take ARMSTRONG PLUMBING LTD. and perform analysis of designations.
        name_first_part = np_svc.name_first_part

        self._designation_any_list = syn_svc.get_designation_any_in_name(name=name_first_part).data
        self._designation_end_list = syn_svc.get_designation_end_in_name(name=name_first_part).data

        self._all_designations = syn_svc.get_designation_all_in_name(name=name_first_part).data

    '''
    Set designations in position <end> found any other place in the company name, these designations are misplaced.
    '''

    def _set_designations_incorrect_position_by_input_name(self):
        syn_svc = self.synonym_service
        tokenized_name = self.get_original_name_tokenized()
        #correct_designation_end_list = remove_periods_designation(self._designation_end_list_correct)
        correct_designation_end_list = self._designation_end_list_correct

        designation_end_misplaced_list = syn_svc.get_incorrect_designation_end_in_name(tokenized_name=tokenized_name,
                                                                                       designation_end_list=correct_designation_end_list).data
        self._misplaced_designation_end_list = designation_end_misplaced_list