import gc
import time
import pandas as pd
import numpy as np


def reshape_for_animations(
    event_log,
    every_x_time_units=10,
    limit_duration=10 * 60 * 24,
    step_snapshot_max=50,
    time_col_name="time",
    entity_col_name="entity_id",
    event_type_col_name="event_type",
    event_col_name="event",
    pathway_col_name=None,
    debug_mode=False,
):
    """
    Reshape event log data for animation purposes.

    This function processes an event log to create a series of snapshots at regular time intervals,
    suitable for creating animations of patient flow through a system.

    Parameters
    ----------
    event_log : pd.DataFrame
        The input event log containing entity events and timestamps in the form of a number of time
        units since the simulation began.
    every_x_time_units : int, optional
        The time interval between snapshots in preferred time units (default is 10).
    limit_duration : int, optional
        The maximum duration to consider in preferred time units (default is 10 days).
    step_snapshot_max : int, optional
        The maximum number of entities to include in each snapshot for each event (default is 50).
    time_col_name : str, default="time"
        Name of the column in `event_log` that contains the timestamp of each event.
        Timestamps should represent the number of time units since the simulation began.
    entity_col_name : str, default="entity_id"
        Name of the column in `event_log` that contains the unique identifier for each entity
        (e.g., "entity_id", "entity", "patient", "patient_id", "customer", "ID").
    event_type_col_name : str, default="event_type"
        Name of the column in `event_log` that specifies the category of the event.
        Supported event types include 'arrival_departure', 'resource_use',
        'resource_use_end', and 'queue'.
    event_col_name : str, default="event"
        Name of the column in `event_log` that specifies the actual event that occurred.
    pathway_col_name : str, optional, default=None
        Name of the column in `event_log` that identifies the specific pathway or
        process flow the entity is following. If `None`, it is assumed that pathway
        information is not present.
    debug_mode : bool, optional
        If True, print debug information during processing (default is False).

    Returns
    -------
    DataFrame
        A reshaped DataFrame containing snapshots of entity positions at regular time intervals,
        sorted by minute and event.

    Notes
    -----
    - The function creates snapshots of entity positions at specified time intervals.
    - It handles entities who are present in the system at each snapshot time.
    - Entities are ranked within each event based on their arrival order.
    - A maximum number of patients per event can be set to limit the number of entities who will be
      displayed on screen within any one event type at a time.
    - An 'exit' event is added for each entity at the end of their journey.
    - The function uses memory management techniques (del and gc.collect()) to handle large datasets.

    TODO
    ----
    - Add behavior for when limit_duration is None.
    - Consider adding 'first step' and 'last step' parameters.
    - Implement pathway order and precedence columns.
    - Fix the automatic exit at the end of the simulation run for all entities.
    """
    entity_dfs = []

    if pathway_col_name is not None:
        pivoted_log = event_log.pivot_table(
            values=time_col_name,
            index=[entity_col_name, event_type_col_name, pathway_col_name],
            columns=event_col_name,
        ).reset_index()

    else:
        pivoted_log = event_log.pivot_table(
            values=time_col_name,
            index=[entity_col_name, event_type_col_name],
            columns=event_col_name,
        ).reset_index()

    # TODO: Add in behaviour for if limit_duration is None

    ################################################################################
    # Iterate through every matching minute
    # and generate snapshot df of position of any entities present at that moment
    ################################################################################
    # Note that we want to do this for everything up to AND INCLUDING the duration
    for time_unit in range(limit_duration + every_x_time_units):
        # print(minute)
        # Get entities who arrived before the current minute and who left the system after the current minute
        # (or arrived but didn't reach the point of being seen before the model run ended)
        # When turning this into a function, think we will want user to pass
        # 'first step' and 'last step' or something similar
        # and will want to reshape the event log for this so that it has a clear start/end regardless
        # of pathway (move all the pathway stuff into a separate column?)

        # Think we maybe need a pathway order and pathway precedence column
        # But what about shared elements of each pathway?
        if time_unit % every_x_time_units == 0:
            try:
                # Work out which entities - if any - were present in the simulation at the current time
                # They will have arrived at or before the minute in question, and they will depart at
                # or after the minute in question, or never depart during our model run
                # (which can happen if they arrive towards the end, or there is a bottleneck)
                current_entities_in_moment = pivoted_log[
                    (pivoted_log["arrival"] <= time_unit)
                    & (
                        (pivoted_log["depart"] >= time_unit)
                        | (pivoted_log["depart"].isnull())
                    )
                ][entity_col_name].values
            except KeyError:
                current_entities_in_moment = []  # Use an empty list for consistency

            # If we do have any entities, they will have been passed as a list
            # so now just filter our event log down to the events these entities have been
            # involved in
            if len(current_entities_in_moment) > 0:
                # Grab just those entities from the filtered log (the unpivoted version)

                # Filter out any events that have taken place after the minute we are interested in

                entity_minute_df = event_log[
                    (event_log[entity_col_name].isin(current_entities_in_moment))
                    & (event_log[time_col_name] <= time_unit)
                ]

                # Each entity can only be in a single place at once

                # TODO: Are there instances where this assumption may be broken, and how would we
                # handle them? e.g. someone who is in a ward but waiting for an x-ray to be read
                # could need to be represented in both queues simultaneously

                # We have filtered out  events that occurred later than the current minute,
                # so filter out any events then just take the latest event that has
                # taken place for each entity
                most_recent_events_time_unit_ungrouped = (
                    entity_minute_df.reset_index(drop=False)
                    .sort_values([time_col_name, "index"], ascending=True)
                    .groupby([entity_col_name])
                    .tail(1)
                )

                # Now rank entities within a given event by the order in which they turned up to that event
                most_recent_events_time_unit_ungrouped["rank"] = (
                    most_recent_events_time_unit_ungrouped.groupby([event_col_name])[
                        "index"
                    ].rank(method="first")
                )

                most_recent_events_time_unit_ungrouped["max"] = (
                    most_recent_events_time_unit_ungrouped.groupby(event_col_name)[
                        "rank"
                    ].transform("max")
                )

                # ----------------------------------------------------------------------------- #

                # Exclude event types that should not be part of snapshot logic
                excluded_types = ["resource_use", "resource_use_end"]

                # Apply snapshot logic per event (assuming 'event_id' identifies each event)
                def process_event_group(df):
                    if df[event_type_col_name].iloc[0] in excluded_types:
                        return df  # Return unchanged
                    else:
                        # Keep only top (step_snapshot_max + 1) ranks
                        df = df[df["rank"] <= (step_snapshot_max + 1)].copy()

                        # Identify max rank row (to possibly add 'additional' column)
                        max_row = df[df["rank"] == float(step_snapshot_max + 1)].copy()
                        if len(max_row) > 0:
                            max_row["additional"] = max_row["max"] - max_row["rank"]
                            df = pd.concat(
                                [
                                    df[df["rank"] != float(step_snapshot_max + 1)],
                                    max_row,
                                ],
                                ignore_index=True,
                            )
                        return df

                # Apply the per-event logic
                most_recent_events_time_unit_ungrouped = (
                    most_recent_events_time_unit_ungrouped.groupby(
                        event_col_name, group_keys=False
                    ).apply(process_event_group)
                )

                # Clean up and store snapshot
                entity_dfs.append(
                    most_recent_events_time_unit_ungrouped.drop(
                        columns="max", errors="ignore"
                    ).assign(snapshot_time=time_unit)
                )

            else:
                # If no entities, append a DataFrame with just the snapshot_time
                # This creates a row with NaN for all other columns, preserving the time step.
                empty_df = pd.DataFrame([{"snapshot_time": time_unit}])
                entity_dfs.append(empty_df)

    if debug_mode:
        print(
            f"Iteration through time-unit-by-time-unit logs complete {time.strftime('%H:%M:%S', time.localtime())}"
        )

    # Join together all entity dfs - so the dataframe created per time snapshot - are put into
    # one large dataframe
    full_entity_df = (pd.concat(entity_dfs, ignore_index=True)).reset_index(drop=True)

    if debug_mode:
        print(
            f"Snapshot df concatenation complete at {time.strftime('%H:%M:%S', time.localtime())}"
        )

    # We no longer need to keep the individual dataframes in that list, so get rid of them
    # to free up memory asap
    del entity_dfs
    gc.collect()

    # Add a final exit step for each client

    # This is helpful as it ensures all patients are visually seen to exit rather than
    # just disappearing after their final step

    # It makes it easier to track the split of people going on to an optional step when
    # this step is at the end of the pathway

    # First, get the last step for every single person
    final_step = (
        full_entity_df.sort_values([entity_col_name, "snapshot_time"], ascending=True)
        .groupby(entity_col_name)
        .tail(1)
        .copy()
    )

    # Propose their 'exit' time
    final_step["snapshot_time"] = final_step["snapshot_time"] + every_x_time_units
    final_step[event_col_name] = "depart"

    # Only keep rows for people whose exit step will happen *before* the simulation end
    final_step = final_step[final_step["snapshot_time"] <= (limit_duration)]

    full_entity_df = pd.concat([full_entity_df, final_step], ignore_index=True)

    del final_step
    gc.collect()

    return (
        full_entity_df.sort_values(["snapshot_time", event_col_name])
        .reset_index(drop=True)
        .dropna(axis=1, how="all")
    )


def generate_animation_df(
    full_entity_df,
    event_position_df,
    wrap_queues_at=20,
    wrap_resources_at=20,
    step_snapshot_max=50,
    gap_between_entities=10,
    gap_between_resources=10,
    gap_between_resource_rows=30,
    gap_between_queue_rows=30,
    time_col_name="time",
    entity_col_name="entity_id",
    event_type_col_name="event_type",
    event_col_name="event",
    resource_col_name="resource_id",
    debug_mode=False,
    custom_entity_icon_list=None,
    include_fun_emojis=False,
):
    """
    Generate a DataFrame for animation purposes by adding position information to entity data.

    This function takes entity event data and adds positional information for visualization,
    handling both queuing and resource use events.

    Parameters
    ----------
    full_entity_df : pd.DataFrame
        Output of reshape_for_animation(), containing entity event data.
    event_position_df : pd.DataFrame
        DataFrame with columns 'event', 'x', and 'y', specifying initial positions for each event type.
    wrap_queues_at : int, optional
        Number of entities in a queue before wrapping to a new row (default is 20).
    wrap_resources_at : int, optional
        Number of resources to show before wrapping to a new row (default is 20).
    step_snapshot_max : int, optional
        Maximum number of patients to show in each snapshot (default is 50).
    gap_between_entities : int, optional
        Horizontal spacing between entities in pixels (default is 10).
    gap_between_resources : int, optional
        Horizontal spacing between resources in pixels (default is 10).
    gap_between_queue_rows : int, optional
        Vertical spacing between rows in pixels (default is 30).
    gap_between_resource_rows : int, optional
        Vertical spacing between rows in pixels (default is 30).
    time_col_name : str, default="time"
        Name of the column in `event_log` that contains the timestamp of each event.
        Timestamps should represent the number of time units since the simulation began.
    entity_col_name : str, default="entity_id"
        Name of the column in `event_log` that contains the unique identifier for each entity
        (e.g., "entity_id", "entity", "patient", "patient_id", "customer", "ID").
    event_type_col_name : str, default="event_type"
        Name of the column in `event_log` that specifies the category of the event.
        Supported event types include 'arrival_departure', 'resource_use',
        'resource_use_end', and 'queue'.
    resource_col_name : str, default="resource_id"
        Name of the column for the resource identifier. Used for 'resource_use' events.
    event_col_name : str, default="event"
        Name of the column in `event_log` that specifies the actual event that occurred.
    debug_mode : bool, optional
        If True, print debug information during processing (default is False).
    custom_entity_icon_list : list, optional
        If provided, will be used as the list for entity icons. Once the end of the list is reached,
        it will loop back around to the beginning (so e.g. if a list of 8 icons is provided, entities
        1 to 8 will use the provided emoji list, and then entity 9 will use the same icon as entity 1,
        and so on.)
    include_fun_emojis : bool, default=False
        If True, include the more 'fun' emojis, such as Santa Claus. Ignored if a custom entity icon list
        is passed.

    Returns
    -------
    pd.DataFrame
        A DataFrame with added columns for x and y positions, and icons for each entity.

    Notes
    -----
    - The function handles both queuing and resource use events differently.
    - It assigns unique icons to entities for visualization.
    - Queues can be wrapped to multiple rows if they exceed a specified length.
    - The function adds a visual indicator for additional entities when exceeding the snapshot limit.

    TODO
    ----
    - Write a test to ensure that no entity ID appears in multiple places at a single time unit.
    """

    # Filter to only a single replication

    # TODO: Write a test  to ensure that no patient ID appears in multiple places at a single time unit
    # and return an error if it does so

    # Order entities within event/time unit to determine their eventual position in the line
    full_entity_df["rank"] = full_entity_df.groupby([event_col_name, "snapshot_time"])[
        "snapshot_time"
    ].rank(method="first")

    full_entity_df_plus_pos = full_entity_df.merge(
        event_position_df, on=event_col_name, how="left"
    ).sort_values([event_col_name, "snapshot_time", time_col_name])

    # Separate the empty snapshots from the entity data
    # We can identify them as rows where the entity ID is null.
    empty_snapshots = full_entity_df_plus_pos[
        full_entity_df_plus_pos[entity_col_name].isnull()
    ].copy()

    entity_data = full_entity_df_plus_pos[
        full_entity_df_plus_pos[entity_col_name].notnull()
    ].copy()

    # Determine the position for any resource use steps
    resource_use = entity_data[
        entity_data[event_type_col_name] == "resource_use"
    ].copy()
    # resource_use['y_final'] =  resource_use['y']

    if len(resource_use) > 0:
        resource_use = resource_use.rename(columns={"y": "y_final"})
        resource_use["x_final"] = (
            resource_use["x"] - resource_use[resource_col_name] * gap_between_resources
        )

        # If we want resources to wrap at a certain queue length, do this here
        # They'll wrap at the defined point and then the queue will start expanding upwards
        # from the starting row
        if wrap_resources_at is not None:
            resource_use["row"] = np.floor(
                (resource_use[resource_col_name] - 1) / (wrap_resources_at)
            )

            resource_use["x_final"] = (
                resource_use["x_final"]
                + (wrap_resources_at * resource_use["row"] * gap_between_resources)
                + gap_between_resources
            )

            resource_use["y_final"] = resource_use["y_final"] + (
                resource_use["row"] * gap_between_resource_rows
            )

    # Determine the position for any queuing steps
    queues = entity_data[entity_data["event_type"] == "queue"].copy()

    # queues['y_final'] =  queues['y']
    queues = queues.rename(columns={"y": "y_final"})
    queues["x_final"] = queues["x"] - queues["rank"] * gap_between_entities

    # If we want people to wrap at a certain queue length, do this here
    # They'll wrap at the defined point and then the queue will start expanding upwards
    # from the starting row
    if wrap_queues_at is not None:
        queues["row"] = np.floor((queues["rank"] - 1) / (wrap_queues_at))

        queues["x_final"] = (
            queues["x_final"]
            + (wrap_queues_at * queues["row"] * gap_between_entities)
            + gap_between_entities
        )

        queues["y_final"] = queues["y_final"] + (queues["row"] * gap_between_queue_rows)

    queues["x_final"] = np.where(
        queues["rank"] != step_snapshot_max + 1,
        queues["x_final"],
        queues["x_final"] - (gap_between_entities * (wrap_queues_at / 2)),
    )

    if len(resource_use) > 0:
        processed_entities_df = pd.concat([queues, resource_use], ignore_index=True)
        del resource_use, queues
    else:
        processed_entities_df = queues.copy()
        del queues

    # Add the empty snapshots back into the main dataframe
    full_entity_df_plus_pos = pd.concat(
        [processed_entities_df, empty_snapshots], ignore_index=True
    )

    if debug_mode:
        print(
            f"Placement dataframe finished construction at {time.strftime('%H:%M:%S', time.localtime())}"
        )

    # full_patient_df_plus_pos['icon'] = '🙍'

    # TODO: Add warnings if duplicates are found (because in theory they shouldn't be)
    individual_entities = (
        full_entity_df[entity_col_name].drop_duplicates().sort_values()
    )

    # Recommend https://emojipedia.org/ for finding emojis to add to list
    # note that best compatibility across systems can be achieved by using
    # emojis from v12.0 and below - Windows 10 got no more updates after that point

    if custom_entity_icon_list is None:
        icon_list = [
            "🧔🏼",
            "👨🏿‍🦯",
            "👨🏻‍🦰",
            "🧑🏻",
            "👩🏿‍🦱",
            "🤰",
            "👳🏽",
            "👩🏼‍🦳",
            "👨🏿‍🦳",
            "👩🏼‍🦱",
            "🧍🏽‍♀️",
            "👨🏼‍🔬",
            "👩🏻‍🦰",
            "🧕🏿",
            "👨🏼‍🦽",
            "👴🏾",
            "👨🏼‍🦱",
            "👷🏾",
            "👧🏿",
            "🙎🏼‍♂️",
            "👩🏻‍🦲",
            "🧔🏾",
            "🧕🏻",
            "👨🏾‍🎓",
            "👨🏾‍🦲",
            "👨🏿‍🦰",
            "🙍🏼‍♂️",
            "🙋🏾‍♀️",
            "👩🏻‍🔧",
            "👨🏿‍🦽",
            "👩🏼‍🦳",
            "👩🏼‍🦼",
            "🙋🏽‍♂️",
            "👩🏿‍🎓",
            "👴🏻",
            "🤷🏻‍♀️",
            "👶🏾",
            "👨🏻‍✈️",
            "🙎🏿‍♀️",
            "👶🏻",
            "👴🏿",
            "👨🏻‍🦳",
            "👩🏽",
            "👩🏽‍🦳",
            "🧍🏼‍♂️",
            "👩🏽‍🎓",
            "👱🏻‍♀️",
            "👲🏼",
            "🧕🏾",
            "👨🏻‍🦯",
            "🧔🏿",
            "👳🏿",
            "🤦🏻‍♂️",
            "👩🏽‍🦰",
            "👨🏼‍✈️",
            "👨🏾‍🦲",
            "🧍🏾‍♂️",
            "👧🏼",
            "🤷🏿‍♂️",
            "👨🏿‍🔧",
            "👱🏾‍♂️",
            "👨🏼‍🎓",
            "👵🏼",
            "🤵🏿",
            "🤦🏾‍♀️",
            "👳🏻",
            "🙋🏼‍♂️",
            "👩🏻‍🎓",
            "👩🏼‍🌾",
            "👩🏾‍🔬",
            "👩🏿‍✈️",
            "👵🏿",
            "🤵🏻",
            "🤰",
        ]

        if include_fun_emojis:
            additional_fun_icon_list = [
                "🎅🏼",
                "👽",
                "🤸",
                "🧜",
                "🏇",
                "🧟",
                "🧞",
                "🧚",
                "🧙",
                "🦹",
                "🦸",
            ]

            icon_list.extend(additional_fun_icon_list)
    else:
        icon_list = custom_entity_icon_list.copy()

    full_icon_list = icon_list * int(np.ceil(len(individual_entities) / len(icon_list)))

    full_icon_list = full_icon_list[0 : len(individual_entities)]

    full_entity_df_plus_pos = full_entity_df_plus_pos.merge(
        pd.DataFrame(
            {entity_col_name: list(individual_entities), "icon": full_icon_list}
        ),
        on=entity_col_name,
    )

    if "additional" in full_entity_df_plus_pos.columns:
        exceeded_snapshot_limit = full_entity_df_plus_pos[
            full_entity_df_plus_pos["additional"].notna()
        ].copy()

        exceeded_snapshot_limit["icon"] = exceeded_snapshot_limit["additional"].apply(
            lambda x: f"+ {int(x):5d} more"
        )

        full_entity_df_plus_pos = pd.concat(
            [
                full_entity_df_plus_pos[full_entity_df_plus_pos["additional"].isna()],
                exceeded_snapshot_limit,
            ],
            ignore_index=True,
        )

    full_entity_df_plus_pos["opacity"] = 1.0

    return full_entity_df_plus_pos.dropna(axis=1, how="all")
