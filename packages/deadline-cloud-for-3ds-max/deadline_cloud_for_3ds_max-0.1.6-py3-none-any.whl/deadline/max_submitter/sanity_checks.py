# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
3ds Max Deadline Cloud Submitter - Sanity checks for job bundle creation
"""

import pymxs  # noqa
from pymxs import runtime as rt

from deadline.max_submitter.utilities import max_utils
from deadline.max_submitter.data_classes import RenderSubmitterUISettings
from deadline.max_submitter.data_const import (
    ALL_CAMERAS_STR,
    ALL_STEREO_CAMERAS_STR,
    ALL_STATE_SETS_STR,
    ALLOWED_RENDERERS,
)


# This is the maximum string length allowed for OJD job parameters.
JOB_PARAMETER_MAX_STRING_LENGTH: int = 1024

# This is the maximum string lenght allowed for OJD step names.
STEP_NAME_MAX_STRING_LENGTH: int = 64


def check_sanity(settings: RenderSubmitterUISettings):
    """
    All sanity checks that need to be performed at submission.

    :param settings: a RenderSubmitterUISettings object containing the latest UI settings
    """
    # Check if 3ds Max scene is saved
    # -> Still needed because you can open a new scene with the UI open
    if not rt.maxFileName:
        raise Exception("Trying to submit unsaved Max scene. Please save " "your scene first.")

    # Check if any unsaved changes were made to the scene and prompt the user to save if not
    rt.checkForSave()

    if len(settings.project_path) > JOB_PARAMETER_MAX_STRING_LENGTH:
        raise Exception(
            f"The project path {settings.project_path} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
        )

    if settings.output_path and len(settings.output_path) > JOB_PARAMETER_MAX_STRING_LENGTH:
        raise Exception(
            f"The setting tab output path {settings.output_path} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
        )

    if rt.rendOutputFilename and len(rt.rendOutputFilename) > JOB_PARAMETER_MAX_STRING_LENGTH:
        raise Exception(
            f"The rendering setup output path {rt.rendOutputFilename} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
        )

    if len(settings.output_name) > JOB_PARAMETER_MAX_STRING_LENGTH:
        raise Exception(
            f"The output filename {settings.output_name} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
        )

    check_sanity_cameras(settings)
    check_sanity_state_sets(settings)

    if settings.override_frame_range:
        if not settings.frame_list:
            raise Exception("Override Frame Range checked but no frame range was given")
        if not max_utils.is_correct_frame_range(settings.frame_list):
            raise Exception(
                "You entered an invalid frame range. Please make sure that the first number in the range "
                "is smaller than the second number. \n"
                "E.g.: 10-5 is invalid, 5-10 is valid."
            )
        if max_utils.get_duplicate_frames(settings.frame_list):
            raise Exception(
                "You entered an invalid frame range. Please make sure there are no duplicate frames in "
                "your range. \n"
                f"Duplicate frames: {max_utils.get_duplicate_frames(settings.frame_list)}"
            )
        if (
            settings.override_frame_range
            and len(settings.frame_list) > JOB_PARAMETER_MAX_STRING_LENGTH
        ):
            raise Exception(
                f"The overriden frame range value {settings.frame_list} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
            )

    if not settings.name:
        raise Exception("No Job Name was given")


def check_sanity_cameras(settings: RenderSubmitterUISettings):
    """
    All camera related sanity checks.

    :param settings: a RenderSubmitterUISettings object containing the latest UI settings
    """
    # Check if there are any cameras in the scene
    cameras = max_utils.get_camera_names()
    if not cameras:
        raise Exception(
            "Trying to submit a scene without a camera. Please"
            " add at least one camera to your scene."
        )

    if (
        settings.camera_selection != ALL_CAMERAS_STR
        and settings.camera_selection != ALL_STEREO_CAMERAS_STR
    ):
        # Check if the selected camera still exists i.e. it wasn't deleted or renamed with the UI open
        if settings.camera_selection not in cameras:
            raise Exception(
                f"{settings.camera_selection} was removed or renamed with the 'Submit to Deadline "
                "Cloud' dialog open. \n"
                "Re-open the dialog to update the 'Cameras To Render' list in the UI."
            )

    for camera in cameras:
        if len(camera) > JOB_PARAMETER_MAX_STRING_LENGTH:
            raise Exception(
                f"The camera name {camera} is too long. The max length allowed is {JOB_PARAMETER_MAX_STRING_LENGTH}."
            )


def check_sanity_state_sets(settings: RenderSubmitterUISettings):
    """
    All state set sanity checks.

    :param settings: a RenderSubmitterUISettings object containing the latest UI settings
    """
    state_sets = max_utils.get_state_set_names()
    state_set_names = [state[0] for state in state_sets]
    if settings.state_set == ALL_STATE_SETS_STR:
        for state_set in state_sets:
            # Set the current state set
            rt.execute(
                f"stateSetsDotNetObject = dotNetObject "
                f'"Autodesk.Max.StateSets.Plugin" \n'
                f"stateSets = stateSetsDotNetObject.Instance \n"
                f"masterState = stateSets.EntityManager.RootEntity."
                f"MasterStateSet \n"
                f"needState = masterState.Children.Item[{state_set[1]}] \n"
                f"masterState.CurrentState = #(needState)"
            )
            check_sanity_specific_state_set(settings, state_set[0])

    else:
        # Check if the selected state set still exists i.e. it wasn't deleted or renamed with the UI open
        if settings.state_set not in state_set_names:
            raise Exception(
                f"{settings.state_set} was removed or renamed with the 'Submit to Deadline Cloud' "
                "dialog open. \n"
                "Re-open the dialog to update the 'State Sets' list in the UI."
            )
        need_state = settings.state_set_index
        # Set the current state set
        rt.execute(
            f"stateSetsDotNetObject = dotNetObject "
            f'"Autodesk.Max.StateSets.Plugin" \n'
            f"stateSets = stateSetsDotNetObject.Instance \n"
            f"masterState = stateSets.EntityManager.RootEntity."
            f"MasterStateSet \n"
            f"needState = masterState.Children.Item[{need_state}]\n"
            f"masterState.CurrentState = #(needState)"
        )
        check_sanity_specific_state_set(settings, settings.state_set)


def check_sanity_specific_state_set(settings: RenderSubmitterUISettings, state_set: str):
    """
    All sanity checks that need to be performed per state set.

    :param settings: a RenderSubmitterUISettings object containing the latest UI settings
    :param state_set: the name of the active state set
    """
    if len(state_set) > STEP_NAME_MAX_STRING_LENGTH:
        raise Exception(
            f"The state set name {state_set} is too long. The max length allowed is {STEP_NAME_MAX_STRING_LENGTH}."
        )

    renderer_name = str(rt.renderers.current).split(":")[0]
    renderer_split_underscore = renderer_name.split("__")[0]
    renderer_split_single_underscore = "_".join(renderer_name.split("_")[:4])

    if (
        renderer_split_underscore not in ALLOWED_RENDERERS
        and renderer_split_single_underscore not in ALLOWED_RENDERERS
    ):
        raise Exception(
            f"{state_set} has an unsupported renderer set. Renderer: " f"{renderer_name}"
        )

    if not settings.override_frame_range:
        # Only check for valid input when pick up frames is selected
        if rt.rendTimeType == 4:
            if not max_utils.is_correct_frame_range(max_utils.get_frames()):
                raise Exception(
                    f"{state_set} has an invalid frame range. Please make sure that the first number in the"
                    " range is smaller than the second number. \n"
                    "E.g.: 10-5 is invalid, 5-10 is valid."
                )
            if max_utils.get_duplicate_frames(max_utils.get_frames()):
                raise Exception(
                    f"{state_set} has an invalid frame range. Please make sure there are no duplicate "
                    "frames in your range. \n"
                    f"Duplicate frames: {max_utils.get_duplicate_frames(max_utils.get_frames())}"
                )

    if not rt.rendOutputFilename:
        if not settings.output_path:
            raise Exception(
                f"Output path for {state_set} isn't set in render settings or in submitter UI"
            )
        if not settings.output_name:
            raise Exception(
                f"Output filename for {state_set} isn't set in render settings or in submitter UI"
            )
