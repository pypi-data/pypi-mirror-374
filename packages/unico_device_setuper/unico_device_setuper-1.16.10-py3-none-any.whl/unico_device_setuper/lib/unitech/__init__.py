from .impl.api.logistic import (
    post_logistic_employee,
    post_logistic_intervention,
    post_logistic_event_export,
    post_logistic_producing_place_pois,
    post_logistic_producer_export,
    post_logistic_realisation,
    post_logistic_producing_place,
    post_logistic_device,
    post_logistic_device_count,
    post_logistic_employee_count,
    post_logistic_producer_count,
    post_logistic_event_count,
    post_logistic_intervention_count,
    post_logistic_realisation_count,
    post_logistic_vehicle,
    post_logistic_administrative_group_export_billing,
    post_logistic_container_pois,
    post_logistic_container_count,
    post_logistic_administrative_group_count,
    post_logistic_producing_place_export,
    post_logistic_producing_place_count,
    post_logistic_event_pois,
    post_logistic_realisation_export,
    post_logistic_event,
    post_logistic_producer,
    post_logistic_administrative_group,
    post_logistic_poi_count,
    post_logistic_administrative_group_export,
    post_logistic_poi,
    post_logistic_intervention_export,
    post_logistic_vehicle_count,
    post_logistic_container_export,
    post_logistic_container,
)
from .impl.api.poi_definition import (
    put_poi_definition_id,
    post_poi_definition,
    get_poi_definition,
)
from .impl.api.outlet_badging import (
    get_outlet_badging_id,
)
from .impl.api.metrics import (
    get_metrics_ping,
    get_metrics_db_status,
)
from .impl.api.intervention import (
    get_intervention_id,
    get_intervention,
    put_intervention_id_planned_date,
    post_intervention_move,
)
from .impl.api.street_service import (
    post_street_service_compute_itinerary,
    post_street_service_transpose,
    post_street_service_compute_itinerary_simplified,
)
from .impl.api.custom_field import (
    post_custom_field,
    get_custom_field,
    delete_custom_field_id,
)
from .impl.api.producer import (
    put_producer_id,
    post_producer,
    get_producer_id,
    get_producer_id_history,
    get_producer_cities,
    get_producer_id_custom_fields,
    get_producer,
    post_producer_delete_many,
)
from .impl.api.contact import (
    get_contact,
)
from .impl.api.depot import (
    put_depot_id_place,
    get_depot_id,
    post_depot,
    get_depot,
    get_depot_id_containers,
    get_depot_id_route_part,
    get_depot_id_details,
)
from .impl.api.contact_definition import (
    put_contact_definition_id,
    get_contact_definition,
    post_contact_definition,
)
from .impl.api.occurrence import (
    put_occurrence_is_locked,
    put_occurrence_itinerary,
    get_occurrence,
    get_occurrence_details,
    get_occurrence_team_by_id,
    get_occurrence_deprecated,
    delete_occurrence,
    get_occurrence_export_collect_points,
    get_occurrence_in_interval,
)
from .impl.api.producing_place_definition import (
    delete_producing_place_definition_id,
    get_producing_place_definition,
    get_producing_place_definition_id,
    post_producing_place_definition,
    put_producing_place_definition_id,
)
from .impl.api.vehicle import (
    get_vehicle_id,
    post_vehicle,
    put_vehicle_id,
    put_vehicle_id_sectors,
    get_vehicle,
    get_vehicle_id_history,
    put_vehicle_archive_many,
    put_vehicle_id_archive,
)
from .impl.api.producing_place import (
    post_producing_place_collectables,
    get_producing_place_related_occurrences_in_interval,
    put_producing_place_id_place,
    put_producing_place_id_update_trackdechets_info,
    get_producing_place_producing_place_id_waste_register,
    get_producing_place_id_history_export,
    post_producing_place_new,
    put_producing_place_id_schedule,
    post_producing_place_many,
    delete_producing_place_anomaly_id,
    get_producing_place_id_images,
    get_producing_place_custom_fields_id,
    get_producing_place_by_id_producer_id,
    get_producing_place_realised_id_details,
    get_producing_place_producing_place_id_schedule,
    get_producing_place_id_history,
    get_producing_place_id_trackdechets_company_info,
    put_producing_place_id_status,
    post_producing_place_by_serial_numbers,
    put_producing_place_info_id,
    put_producing_place_linked_producers,
    put_producing_place_sectors_id,
    post_producing_place_delete_many,
    post_producing_place_collectables_batch,
    post_producing_place_unique_stream_containers_total_by_ids,
    get_producing_place_id_details,
    post_producing_place_id_collection_planning,
)
from .impl.api.administrative_group_definition import (
    get_administrative_group_definition,
    post_administrative_group_definition,
    put_administrative_group_definition_id,
)
from .impl.api.check_in_submit import (
    get_check_in_submit_id,
)
from .impl.api.auth import (
    post_auth_accessible_clients,
    post_auth_enabled_clients,
    post_auth_device_register_device,
    put_auth_reset_password,
    post_auth_change_client,
    put_auth_update_password,
    post_auth_token,
    get_auth_device_login,
)
from .impl.api.driver import (
    get_driver,
)
from .impl.api.sector import (
    delete_sector_id,
    get_sector,
    post_sector,
)
from .impl.api.notification import (
    get_notification_id,
    put_notification_many,
    post_notification,
    get_notification,
)
from .impl.api.comment import (
    put_comment_id,
    post_comment,
    get_comment,
    delete_comment_id,
)
from .impl.api.attachment import (
    delete_attachment_id,
    put_attachment_id,
    post_attachment,
    get_attachment_id_content,
    get_attachment,
)
from .impl.api.vehicle_profile import (
    get_vehicle_profile,
    put_vehicle_profile_id,
    post_vehicle_profile,
)
from .impl.api.stream import (
    post_stream,
    get_stream,
    put_stream_id,
)
from .impl.api.trackdechets_waste_stream import (
    delete_trackdechets_waste_stream_id,
    post_trackdechets_waste_stream,
    get_trackdechets_waste_stream,
    put_trackdechets_waste_stream_id,
)
from .impl.api.segment import (
    get_segment_id,
    get_segment,
)
from .impl.api.user_role import (
    delete_user_role_id,
    post_user_role,
    put_user_role_id,
    get_user_role,
)
from .impl.api.pdf import (
    get_pdf_intervention_mission_orders_response_type,
    get_pdf_roadmap_response_type,
    get_pdf_producing_place_id_realisations,
    get_pdf_waste_transport_document_response_type,
    get_pdf_intervention_destruction_certificates_response_type,
    get_pdf_intervention_elise_commercial_support_documents_response_type,
    get_pdf_intervention_delivery_notice_response_type,
    get_pdf_commercial_support_document_response_type,
)
from .impl.api.producing_place_constraint import (
    put_producing_place_constraint,
    get_producing_place_constraint_id,
)
from .impl.api.container_realised import (
    put_container_realised_id,
    post_container_realised,
    get_container_realised_id,
)
from .impl.api.message import (
    post_message,
)
from .impl.api.bsd import (
    get_bsd_id_download_link,
    get_bsd_client_siret,
)
from .impl.api.round_update import (
    get_round_update_id,
)
from .impl.api.user import (
    put_user_id,
    delete_user_id,
    get_user,
    post_user,
    get_user_username,
)
from .impl.api.geocoding import (
    get_geocoding_by_position,
    get_geocoding_by_address,
)
from .impl.api.dashboard import (
    get_dashboard_stats,
)
from .impl.api.street_service_municipality import (
    get_street_service_municipality,
)
from .impl.api.poi import (
    get_poi_id,
    post_poi,
    put_poi_id,
    get_poi,
    get_poi_id_route_part,
)
from .impl.api.route_part import (
    get_route_part_event_id,
    post_route_part_producing_place_in_polygon,
    post_route_part_segment_in_line,
    post_route_part_availabilities,
    post_route_part_segment_in_polygon,
    get_route_part_producing_place_id,
    get_route_part_segment_id,
    put_route_part_move_many,
    post_route_part_event_in_polygon,
)
from .impl.api.street_service_vehicle_profile import (
    get_street_service_vehicle_profile,
)
from .impl.api.container import (
    put_container_id,
    post_container_many,
    get_container_id_history_export,
    post_container_in_ids,
    get_container_by_reference_reference,
    get_container_id_custom_fields,
    delete_container_id,
    get_container_id_history,
    post_container,
    get_container_id,
    post_container_delete_many,
)
from .impl.api.outlet import (
    get_outlet_id_history,
    get_outlet_id_batches,
    post_outlet,
    get_outlet_id_details,
    get_outlet,
    put_outlet_id,
    get_outlet_id_route_part,
    get_outlet_id,
    get_outlet_route_parts,
)
from .impl.api.uni_and_co_user import (
    post_uni_and_co_user,
)
from .impl.api.public import (
    get_public_badges,
    post_public_event,
    get_public_containers,
    get_public_outlets,
    get_public_realisation_id_track,
    get_public_realisations,
    get_public_event_definition,
    post_public_outlet_badging,
    get_public_producing_place,
    get_public_producing_place_id,
    get_public_v2_containers,
    get_public_check_in_submit,
    get_public_events,
)
from .impl.api.outlet_realised import (
    get_outlet_realised_id,
    delete_outlet_realised_id,
    put_outlet_realised_id,
    post_outlet_realised,
)
from .impl.api.vehicle_loading_type import (
    post_vehicle_loading_type,
    get_vehicle_loading_type,
    put_vehicle_loading_type_id,
)
from .impl.api.realisation import (
    get_realisation_id_collect_report,
    get_realisation_id_planified_vs_realised,
    put_realisation_id,
    get_realisation_id_itinerary_realised,
    post_realisation_delete_many,
    get_realisation_id_containers_realised,
    get_realisation_filter_options,
    get_realisation_id_history,
)
from .impl.api.user_preferences import (
    get_user_preferences_container_sheet_params,
    put_user_preferences_pdf_export_params,
    put_user_preferences_container_sheet_param,
    get_user_preferences_administrative_group_sheet_params,
    get_user_preferences_logistic_params,
    put_user_preferences_administrative_group_sheet_param,
    put_user_preferences_producer_sheet_param,
    get_user_preferences_producer_sheet_params,
    get_user_preferences_pdf_export_params,
    put_user_preferences_operational_tabs_params,
    put_user_preferences_logistic_params_column,
    put_user_preferences_logistic_params_tab,
    get_user_preferences_operational_tabs_params,
)
from .impl.api.event_definition import (
    post_event_definition,
    put_event_definition_id,
    get_event_definition,
)
from .impl.api.icons import (
    get_icons,
)
from .impl.api.map_comment import (
    get_map_comment,
    put_map_comment,
    delete_map_comment_id,
)
from .impl.api.mapbox_tile import (
    get_mapbox_tile,
)
from .impl.api.round_ import (
    get_round_itinerary_planified_id_itinerary,
    get_round_id_future_occurrence_updates_dates,
    get_round_itinerary_route_parts_id_geo_json,
    delete_round_id_round,
    post_round_itineraries_type,
    get_round_itinerary_track_id_geo_json,
    delete_round_occurrence,
    get_round_itinerary_availability_id_itinerary_date,
    get_round_itinerary_realised_id_itinerary,
    post_round_tracks,
    get_round_itinerary_route_parts_id_shp,
    post_round_new,
    post_round_itinerary_route_parts_type,
    put_round,
    get_round_occurrence_details_by_id,
    get_round_itinerary_track_id_shp,
    put_round_round_slots_id_round,
    get_round_team,
)
from .impl.api.rotation_history import (
    post_rotation_history,
    get_rotation_history,
)
from .impl.api.container_definition import (
    put_container_definition_id,
    post_container_definition,
    get_container_definition,
)
from .impl.api.administrative_group import (
    get_administrative_group_id_picture,
    get_administrative_group_id_children,
    get_administrative_group,
    get_administrative_group_id,
    get_administrative_group_id_badges,
    post_administrative_group_delete_many,
    post_administrative_group,
    put_administrative_group_id,
    get_administrative_group_id_custom_fields,
    get_administrative_group_id_history,
    post_administrative_group_id_history_export,
    get_administrative_group_count,
)
from .impl.api.device import (
    get_device_v2_itinerary_id,
    get_device_search_producing_place,
    get_device_v_2_near_by_producing_place,
    get_device_all_devices,
    get_device_poi_definitions,
    post_device_submit_check_in,
    get_device_producing_place_id,
    get_device_drivers,
    get_device_cities,
    get_device_outlets,
    get_device_streams,
    post_device_bsd_sign_many,
    get_device_client_dasri_allow_taken_producing_place_id,
    get_device_event_definitions_categories,
    get_device_task_definitions,
    get_device_near_by_producing_place,
    get_device_producing_place_custom_fields,
    post_device_live_data_update,
    get_device_pre_authenticated_urls,
    post_device_v2_bsd_create,
    put_device_client,
    get_device_containers_by_producing_place_id_id,
    get_device_operators,
    get_device_producing_place_by_container_reference,
    get_device_vehicles,
    get_device_event_definitions,
    get_device_round_id_itinerary,
    get_device_container_by_serial_number_reference,
    get_device_check_in_form,
    get_device_itinerary_id,
    get_device_client,
    get_device_pois_id_poi_definition,
    get_device_container_definitions,
    post_device_uninav_version,
    get_device_map_comments,
    post_device_dasri_sign_many,
    get_device_update_change_log,
    delete_device_event_id,
    get_device_depots,
    get_device_rounds_meta,
    get_device_map_corrections,
)
from .impl.api.external_realisation import (
    get_external_realisation_id_history,
    post_external_realisation_many,
    get_external_realisation_id_track,
)
from .impl.api.user_event_definition_email_subscription import (
    get_user_event_definition_email_subscription,
    post_user_event_definition_email_subscription,
    delete_user_event_definition_email_subscription,
)
from .impl.api.legal_status import (
    get_legal_status,
)
from .impl.api.external import (
    post_external_elise_producing_place,
    post_external_v2_live_vehicle_data,
    post_external_create_ifm_itinerary_id_realisation,
    post_external_elise_interventions,
    post_external_live_vehicle_data,
    get_external_elise_auth_id_franchise,
    get_external_nicollin_ecorec,
    get_external_elise_export,
    post_external_alpes_mesure_filling_rate,
)
from .impl.api.producing_place_realised import (
    get_producing_place_realised_id,
    put_producing_place_realised_id,
)
from .impl.api.operational import (
    post_operational_layers_data_source,
    get_operational_filter_options,
)
from .impl.api.place import (
    get_place_cities,
    get_place,
    put_place_id,
    get_place_id,
)
from .impl.api.waste_batch import (
    post_waste_batch,
)
from .impl.api.employee import (
    put_employee_id_constraint,
    get_employee_id_constraint,
    put_employee_id_schedule,
    get_employee_id_history,
    put_employee_id,
    get_employee_id,
    get_employee_id_schedule,
    put_employee_archive_many,
    post_employee,
)
from .impl.api.itinerary_planified import (
    get_itinerary_planified,
    get_itinerary_planified_id,
    delete_itinerary_planified_id,
)
from .impl.api.map_correction import (
    get_map_correction,
    delete_map_correction_id,
    post_map_correction,
)
from .impl.api.event import (
    get_event,
    post_event_delete_many,
    post_event,
    get_event_id,
    put_event_id,
)
from .impl.api.client import (
    put_client_id,
    get_client_id,
    get_client,
)
from .impl.api.tag import (
    post_tag,
    get_tag_id,
    put_tag_id,
    get_tag,
    delete_tag_id,
)
from .impl.api.operator import (
    get_operator,
)
from .impl.api.itinerary_template import (
    post_itinerary_template,
    put_itinerary_template_id,
    get_itinerary_template,
    get_itinerary_template_id,
)
from .impl.api.event_definition_category import (
    get_event_definition_category,
    post_event_definition_category,
    delete_event_definition_category_id,
    put_event_definition_category_id,
)
from .impl.api.badge import (
    post_badge,
    put_badge_id,
    get_badge,
    get_badge_id,
    get_badge_id_history,
)
from .impl.models.accessible_clients_payload import AccessibleClientsPayload
from .impl.models.accessible_clients_response_item import AccessibleClientsResponseItem
from .impl.models.change_client_payload import ChangeClientPayload
from .impl.models.change_client_response import ChangeClientResponse
from .impl.models.changelog_response import ChangelogResponse
from .impl.models.client_response import ClientResponse
from .impl.models.current_user_response import CurrentUserResponse
from .impl.models.delete_container_id_body import DeleteContainerIdBody
from .impl.models.delete_round_id_round_body import DeleteRoundIdRoundBody
from .impl.models.get_depots_response_item import GetDepotsResponseItem
from .impl.models.get_outlets_response_item import GetOutletsResponseItem
from .impl.models.get_pois_response_item import GetPoisResponseItem
from .impl.models.get_pois_response_item_place import GetPoisResponseItemPlace
from .impl.models.get_pois_response_item_poi_definition import GetPoisResponseItemPoiDefinition
from .impl.models.itinerary_creation_data import ItineraryCreationData
from .impl.models.poi_route_part import PoiRoutePart
from .impl.models.poi_route_part_producing_place import PoiRoutePartProducingPlace
from .impl.models.poi_route_part_state import PoiRoutePartState
from .impl.models.poi_route_part_type import PoiRoutePartType
from .impl.models.post_administrative_group_id_history_export_body import PostAdministrativeGroupIdHistoryExportBody
from .impl.models.post_attachment_body import PostAttachmentBody
from .impl.models.post_badge_body import PostBadgeBody
from .impl.models.post_comment_body import PostCommentBody
from .impl.models.post_container_delete_many_body import PostContainerDeleteManyBody
from .impl.models.post_container_many_body import PostContainerManyBody
from .impl.models.post_container_realised_body import PostContainerRealisedBody
from .impl.models.post_custom_field_body import PostCustomFieldBody
from .impl.models.post_device_live_data_update_body import PostDeviceLiveDataUpdateBody
from .impl.models.post_device_submit_check_in_body import PostDeviceSubmitCheckInBody
from .impl.models.post_device_uninav_version_body import PostDeviceUninavVersionBody
from .impl.models.post_event_definition_body import PostEventDefinitionBody
from .impl.models.post_event_definition_category_body import PostEventDefinitionCategoryBody
from .impl.models.post_external_create_ifm_itinerary_id_realisation_body import PostExternalCreateIFMItineraryIdRealisationBody
from .impl.models.post_external_live_vehicle_data_body import PostExternalLiveVehicleDataBody
from .impl.models.post_intervention_move_body import PostInterventionMoveBody
from .impl.models.post_itinerary_template_body import PostItineraryTemplateBody
from .impl.models.post_logistic_administrative_group_export_billing_body import PostLogisticAdministrativeGroupExportBillingBody
from .impl.models.post_map_correction_body import PostMapCorrectionBody
from .impl.models.post_operational_layers_data_source_body import PostOperationalLayersDataSourceBody
from .impl.models.post_outlet_realised_body import PostOutletRealisedBody
from .impl.models.post_poi_definition_body import PostPoiDefinitionBody
from .impl.models.post_producer_delete_many_body import PostProducerDeleteManyBody
from .impl.models.post_producing_place_by_serial_numbers_body import PostProducingPlaceBySerialNumbersBody
from .impl.models.post_producing_place_collectables_batch_body import PostProducingPlaceCollectablesBatchBody
from .impl.models.post_producing_place_collectables_body import PostProducingPlaceCollectablesBody
from .impl.models.post_producing_place_delete_many_body import PostProducingPlaceDeleteManyBody
from .impl.models.post_producing_place_id_collection_planning_body import PostProducingPlaceIdCollectionPlanningBody
from .impl.models.post_producing_place_many_body import PostProducingPlaceManyBody
from .impl.models.post_producing_place_unique_stream_containers_total_by_ids_body import PostProducingPlaceUniqueStreamContainersTotalByIdsBody
from .impl.models.post_realisation_delete_many_body import PostRealisationDeleteManyBody
from .impl.models.post_rotation_history_body import PostRotationHistoryBody
from .impl.models.post_round_tracks_body import PostRoundTracksBody
from .impl.models.post_route_part_availabilities_body import PostRoutePartAvailabilitiesBody
from .impl.models.post_route_part_event_in_polygon_body import PostRoutePartEventInPolygonBody
from .impl.models.post_route_part_producing_place_in_polygon_body import PostRoutePartProducingPlaceInPolygonBody
from .impl.models.post_route_part_segment_in_line_body import PostRoutePartSegmentInLineBody
from .impl.models.post_route_part_segment_in_polygon_body import PostRoutePartSegmentInPolygonBody
from .impl.models.post_sector_body import PostSectorBody
from .impl.models.post_stream_body import PostStreamBody
from .impl.models.post_street_service_transpose_body import PostStreetServiceTransposeBody
from .impl.models.post_uni_and_co_user_body import PostUniAndCoUserBody
from .impl.models.post_user_body import PostUserBody
from .impl.models.post_user_event_definition_email_subscription_body import PostUserEventDefinitionEmailSubscriptionBody
from .impl.models.post_user_role_body import PostUserRoleBody
from .impl.models.post_vehicle_loading_type_body import PostVehicleLoadingTypeBody
from .impl.models.post_vehicle_profile_body import PostVehicleProfileBody
from .impl.models.post_waste_batch_body import PostWasteBatchBody
from .impl.models.put_attachment_id_body import PutAttachmentIdBody
from .impl.models.put_auth_reset_password_body import PutAuthResetPasswordBody
from .impl.models.put_auth_update_password_body import PutAuthUpdatePasswordBody
from .impl.models.put_badge_id_body import PutBadgeIdBody
from .impl.models.put_comment_id_body import PutCommentIdBody
from .impl.models.put_container_id_body import PutContainerIdBody
from .impl.models.put_container_realised_id_body import PutContainerRealisedIdBody
from .impl.models.put_depot_id_place_body import PutDepotIdPlaceBody
from .impl.models.put_device_client_body import PutDeviceClientBody
from .impl.models.put_employee_archive_many_body import PutEmployeeArchiveManyBody
from .impl.models.put_employee_id_body import PutEmployeeIdBody
from .impl.models.put_employee_id_constraint_body import PutEmployeeIdConstraintBody
from .impl.models.put_event_definition_category_id_body import PutEventDefinitionCategoryIdBody
from .impl.models.put_event_definition_id_body import PutEventDefinitionIdBody
from .impl.models.put_intervention_id_planned_date_body import PutInterventionIdPlannedDateBody
from .impl.models.put_itinerary_template_id_body import PutItineraryTemplateIdBody
from .impl.models.put_map_comment_body import PutMapCommentBody
from .impl.models.put_occurrence_itinerary_body import PutOccurrenceItineraryBody
from .impl.models.put_outlet_id_body import PutOutletIdBody
from .impl.models.put_place_id_body import PutPlaceIdBody
from .impl.models.put_poi_definition_id_body import PutPoiDefinitionIdBody
from .impl.models.put_producing_place_constraint_body import PutProducingPlaceConstraintBody
from .impl.models.put_producing_place_id_place_body import PutProducingPlaceIdPlaceBody
from .impl.models.put_producing_place_id_status_body import PutProducingPlaceIdStatusBody
from .impl.models.put_producing_place_linked_producers_body import PutProducingPlaceLinkedProducersBody
from .impl.models.put_producing_place_realised_id_body import PutProducingPlaceRealisedIdBody
from .impl.models.put_round_body import PutRoundBody
from .impl.models.put_round_round_slots_id_round_body import PutRoundRoundSlotsIdRoundBody
from .impl.models.put_route_part_move_many_body import PutRoutePartMoveManyBody
from .impl.models.put_stream_id_body import PutStreamIdBody
from .impl.models.put_tag_id_body import PutTagIdBody
from .impl.models.put_user_id_body import PutUserIdBody
from .impl.models.put_user_preferences_logistic_params_column_body import PutUserPreferencesLogisticParamsColumnBody
from .impl.models.put_user_preferences_operational_tabs_params_body import PutUserPreferencesOperationalTabsParamsBody
from .impl.models.put_user_preferences_pdf_export_params_body import PutUserPreferencesPdfExportParamsBody
from .impl.models.put_user_role_id_body import PutUserRoleIdBody
from .impl.models.register_device_payload import RegisterDevicePayload
from .impl.models.register_device_response import RegisterDeviceResponse
from .impl.models.round_creation_data import RoundCreationData
from .impl.models.round_creation_data_type import RoundCreationDataType
from .impl.models.round_slot_data import RoundSlotData
from .impl.models.round_slot_data_recurrence_type import RoundSlotDataRecurrenceType
from .impl.models.segment_route_part import SegmentRoutePart
from .impl.models.segment_route_part_direction import SegmentRoutePartDirection
from .impl.models.segment_route_part_intervention_mode import SegmentRoutePartInterventionMode
from .impl.models.segment_route_part_side import SegmentRoutePartSide
from .impl.models.segment_route_part_state import SegmentRoutePartState
from .impl.models.segment_route_part_type import SegmentRoutePartType
from .impl.models.token_payload import TokenPayload
from .impl.models.token_response import TokenResponse
from .impl.client import Client
__all__ = [
    'post_logistic_employee',
    'post_logistic_intervention',
    'post_logistic_event_export',
    'post_logistic_producing_place_pois',
    'post_logistic_producer_export',
    'post_logistic_realisation',
    'post_logistic_producing_place',
    'post_logistic_device',
    'post_logistic_device_count',
    'post_logistic_employee_count',
    'post_logistic_producer_count',
    'post_logistic_event_count',
    'post_logistic_intervention_count',
    'post_logistic_realisation_count',
    'post_logistic_vehicle',
    'post_logistic_administrative_group_export_billing',
    'post_logistic_container_pois',
    'post_logistic_container_count',
    'post_logistic_administrative_group_count',
    'post_logistic_producing_place_export',
    'post_logistic_producing_place_count',
    'post_logistic_event_pois',
    'post_logistic_realisation_export',
    'post_logistic_event',
    'post_logistic_producer',
    'post_logistic_administrative_group',
    'post_logistic_poi_count',
    'post_logistic_administrative_group_export',
    'post_logistic_poi',
    'post_logistic_intervention_export',
    'post_logistic_vehicle_count',
    'post_logistic_container_export',
    'post_logistic_container',
    'put_poi_definition_id',
    'post_poi_definition',
    'get_poi_definition',
    'get_outlet_badging_id',
    'get_metrics_ping',
    'get_metrics_db_status',
    'get_intervention_id',
    'get_intervention',
    'put_intervention_id_planned_date',
    'post_intervention_move',
    'post_street_service_compute_itinerary',
    'post_street_service_transpose',
    'post_street_service_compute_itinerary_simplified',
    'post_custom_field',
    'get_custom_field',
    'delete_custom_field_id',
    'put_producer_id',
    'post_producer',
    'get_producer_id',
    'get_producer_id_history',
    'get_producer_cities',
    'get_producer_id_custom_fields',
    'get_producer',
    'post_producer_delete_many',
    'get_contact',
    'put_depot_id_place',
    'get_depot_id',
    'post_depot',
    'get_depot',
    'get_depot_id_containers',
    'get_depot_id_route_part',
    'get_depot_id_details',
    'put_contact_definition_id',
    'get_contact_definition',
    'post_contact_definition',
    'put_occurrence_is_locked',
    'put_occurrence_itinerary',
    'get_occurrence',
    'get_occurrence_details',
    'get_occurrence_team_by_id',
    'get_occurrence_deprecated',
    'delete_occurrence',
    'get_occurrence_export_collect_points',
    'get_occurrence_in_interval',
    'delete_producing_place_definition_id',
    'get_producing_place_definition',
    'get_producing_place_definition_id',
    'post_producing_place_definition',
    'put_producing_place_definition_id',
    'get_vehicle_id',
    'post_vehicle',
    'put_vehicle_id',
    'put_vehicle_id_sectors',
    'get_vehicle',
    'get_vehicle_id_history',
    'put_vehicle_archive_many',
    'put_vehicle_id_archive',
    'post_producing_place_collectables',
    'get_producing_place_related_occurrences_in_interval',
    'put_producing_place_id_place',
    'put_producing_place_id_update_trackdechets_info',
    'get_producing_place_producing_place_id_waste_register',
    'get_producing_place_id_history_export',
    'post_producing_place_new',
    'put_producing_place_id_schedule',
    'post_producing_place_many',
    'delete_producing_place_anomaly_id',
    'get_producing_place_id_images',
    'get_producing_place_custom_fields_id',
    'get_producing_place_by_id_producer_id',
    'get_producing_place_realised_id_details',
    'get_producing_place_producing_place_id_schedule',
    'get_producing_place_id_history',
    'get_producing_place_id_trackdechets_company_info',
    'put_producing_place_id_status',
    'post_producing_place_by_serial_numbers',
    'put_producing_place_info_id',
    'put_producing_place_linked_producers',
    'put_producing_place_sectors_id',
    'post_producing_place_delete_many',
    'post_producing_place_collectables_batch',
    'post_producing_place_unique_stream_containers_total_by_ids',
    'get_producing_place_id_details',
    'post_producing_place_id_collection_planning',
    'get_administrative_group_definition',
    'post_administrative_group_definition',
    'put_administrative_group_definition_id',
    'get_check_in_submit_id',
    'post_auth_accessible_clients',
    'post_auth_enabled_clients',
    'post_auth_device_register_device',
    'put_auth_reset_password',
    'post_auth_change_client',
    'put_auth_update_password',
    'post_auth_token',
    'get_auth_device_login',
    'get_driver',
    'delete_sector_id',
    'get_sector',
    'post_sector',
    'get_notification_id',
    'put_notification_many',
    'post_notification',
    'get_notification',
    'put_comment_id',
    'post_comment',
    'get_comment',
    'delete_comment_id',
    'delete_attachment_id',
    'put_attachment_id',
    'post_attachment',
    'get_attachment_id_content',
    'get_attachment',
    'get_vehicle_profile',
    'put_vehicle_profile_id',
    'post_vehicle_profile',
    'post_stream',
    'get_stream',
    'put_stream_id',
    'delete_trackdechets_waste_stream_id',
    'post_trackdechets_waste_stream',
    'get_trackdechets_waste_stream',
    'put_trackdechets_waste_stream_id',
    'get_segment_id',
    'get_segment',
    'delete_user_role_id',
    'post_user_role',
    'put_user_role_id',
    'get_user_role',
    'get_pdf_intervention_mission_orders_response_type',
    'get_pdf_roadmap_response_type',
    'get_pdf_producing_place_id_realisations',
    'get_pdf_waste_transport_document_response_type',
    'get_pdf_intervention_destruction_certificates_response_type',
    'get_pdf_intervention_elise_commercial_support_documents_response_type',
    'get_pdf_intervention_delivery_notice_response_type',
    'get_pdf_commercial_support_document_response_type',
    'put_producing_place_constraint',
    'get_producing_place_constraint_id',
    'put_container_realised_id',
    'post_container_realised',
    'get_container_realised_id',
    'post_message',
    'get_bsd_id_download_link',
    'get_bsd_client_siret',
    'get_round_update_id',
    'put_user_id',
    'delete_user_id',
    'get_user',
    'post_user',
    'get_user_username',
    'get_geocoding_by_position',
    'get_geocoding_by_address',
    'get_dashboard_stats',
    'get_street_service_municipality',
    'get_poi_id',
    'post_poi',
    'put_poi_id',
    'get_poi',
    'get_poi_id_route_part',
    'get_route_part_event_id',
    'post_route_part_producing_place_in_polygon',
    'post_route_part_segment_in_line',
    'post_route_part_availabilities',
    'post_route_part_segment_in_polygon',
    'get_route_part_producing_place_id',
    'get_route_part_segment_id',
    'put_route_part_move_many',
    'post_route_part_event_in_polygon',
    'get_street_service_vehicle_profile',
    'put_container_id',
    'post_container_many',
    'get_container_id_history_export',
    'post_container_in_ids',
    'get_container_by_reference_reference',
    'get_container_id_custom_fields',
    'delete_container_id',
    'get_container_id_history',
    'post_container',
    'get_container_id',
    'post_container_delete_many',
    'get_outlet_id_history',
    'get_outlet_id_batches',
    'post_outlet',
    'get_outlet_id_details',
    'get_outlet',
    'put_outlet_id',
    'get_outlet_id_route_part',
    'get_outlet_id',
    'get_outlet_route_parts',
    'post_uni_and_co_user',
    'get_public_badges',
    'post_public_event',
    'get_public_containers',
    'get_public_outlets',
    'get_public_realisation_id_track',
    'get_public_realisations',
    'get_public_event_definition',
    'post_public_outlet_badging',
    'get_public_producing_place',
    'get_public_producing_place_id',
    'get_public_v2_containers',
    'get_public_check_in_submit',
    'get_public_events',
    'get_outlet_realised_id',
    'delete_outlet_realised_id',
    'put_outlet_realised_id',
    'post_outlet_realised',
    'post_vehicle_loading_type',
    'get_vehicle_loading_type',
    'put_vehicle_loading_type_id',
    'get_realisation_id_collect_report',
    'get_realisation_id_planified_vs_realised',
    'put_realisation_id',
    'get_realisation_id_itinerary_realised',
    'post_realisation_delete_many',
    'get_realisation_id_containers_realised',
    'get_realisation_filter_options',
    'get_realisation_id_history',
    'get_user_preferences_container_sheet_params',
    'put_user_preferences_pdf_export_params',
    'put_user_preferences_container_sheet_param',
    'get_user_preferences_administrative_group_sheet_params',
    'get_user_preferences_logistic_params',
    'put_user_preferences_administrative_group_sheet_param',
    'put_user_preferences_producer_sheet_param',
    'get_user_preferences_producer_sheet_params',
    'get_user_preferences_pdf_export_params',
    'put_user_preferences_operational_tabs_params',
    'put_user_preferences_logistic_params_column',
    'put_user_preferences_logistic_params_tab',
    'get_user_preferences_operational_tabs_params',
    'post_event_definition',
    'put_event_definition_id',
    'get_event_definition',
    'get_icons',
    'get_map_comment',
    'put_map_comment',
    'delete_map_comment_id',
    'get_mapbox_tile',
    'get_round_itinerary_planified_id_itinerary',
    'get_round_id_future_occurrence_updates_dates',
    'get_round_itinerary_route_parts_id_geo_json',
    'delete_round_id_round',
    'post_round_itineraries_type',
    'get_round_itinerary_track_id_geo_json',
    'delete_round_occurrence',
    'get_round_itinerary_availability_id_itinerary_date',
    'get_round_itinerary_realised_id_itinerary',
    'post_round_tracks',
    'get_round_itinerary_route_parts_id_shp',
    'post_round_new',
    'post_round_itinerary_route_parts_type',
    'put_round',
    'get_round_occurrence_details_by_id',
    'get_round_itinerary_track_id_shp',
    'put_round_round_slots_id_round',
    'get_round_team',
    'post_rotation_history',
    'get_rotation_history',
    'put_container_definition_id',
    'post_container_definition',
    'get_container_definition',
    'get_administrative_group_id_picture',
    'get_administrative_group_id_children',
    'get_administrative_group',
    'get_administrative_group_id',
    'get_administrative_group_id_badges',
    'post_administrative_group_delete_many',
    'post_administrative_group',
    'put_administrative_group_id',
    'get_administrative_group_id_custom_fields',
    'get_administrative_group_id_history',
    'post_administrative_group_id_history_export',
    'get_administrative_group_count',
    'get_device_v2_itinerary_id',
    'get_device_search_producing_place',
    'get_device_v_2_near_by_producing_place',
    'get_device_all_devices',
    'get_device_poi_definitions',
    'post_device_submit_check_in',
    'get_device_producing_place_id',
    'get_device_drivers',
    'get_device_cities',
    'get_device_outlets',
    'get_device_streams',
    'post_device_bsd_sign_many',
    'get_device_client_dasri_allow_taken_producing_place_id',
    'get_device_event_definitions_categories',
    'get_device_task_definitions',
    'get_device_near_by_producing_place',
    'get_device_producing_place_custom_fields',
    'post_device_live_data_update',
    'get_device_pre_authenticated_urls',
    'post_device_v2_bsd_create',
    'put_device_client',
    'get_device_containers_by_producing_place_id_id',
    'get_device_operators',
    'get_device_producing_place_by_container_reference',
    'get_device_vehicles',
    'get_device_event_definitions',
    'get_device_round_id_itinerary',
    'get_device_container_by_serial_number_reference',
    'get_device_check_in_form',
    'get_device_itinerary_id',
    'get_device_client',
    'get_device_pois_id_poi_definition',
    'get_device_container_definitions',
    'post_device_uninav_version',
    'get_device_map_comments',
    'post_device_dasri_sign_many',
    'get_device_update_change_log',
    'delete_device_event_id',
    'get_device_depots',
    'get_device_rounds_meta',
    'get_device_map_corrections',
    'get_external_realisation_id_history',
    'post_external_realisation_many',
    'get_external_realisation_id_track',
    'get_user_event_definition_email_subscription',
    'post_user_event_definition_email_subscription',
    'delete_user_event_definition_email_subscription',
    'get_legal_status',
    'post_external_elise_producing_place',
    'post_external_v2_live_vehicle_data',
    'post_external_create_ifm_itinerary_id_realisation',
    'post_external_elise_interventions',
    'post_external_live_vehicle_data',
    'get_external_elise_auth_id_franchise',
    'get_external_nicollin_ecorec',
    'get_external_elise_export',
    'post_external_alpes_mesure_filling_rate',
    'get_producing_place_realised_id',
    'put_producing_place_realised_id',
    'post_operational_layers_data_source',
    'get_operational_filter_options',
    'get_place_cities',
    'get_place',
    'put_place_id',
    'get_place_id',
    'post_waste_batch',
    'put_employee_id_constraint',
    'get_employee_id_constraint',
    'put_employee_id_schedule',
    'get_employee_id_history',
    'put_employee_id',
    'get_employee_id',
    'get_employee_id_schedule',
    'put_employee_archive_many',
    'post_employee',
    'get_itinerary_planified',
    'get_itinerary_planified_id',
    'delete_itinerary_planified_id',
    'get_map_correction',
    'delete_map_correction_id',
    'post_map_correction',
    'get_event',
    'post_event_delete_many',
    'post_event',
    'get_event_id',
    'put_event_id',
    'put_client_id',
    'get_client_id',
    'get_client',
    'post_tag',
    'get_tag_id',
    'put_tag_id',
    'get_tag',
    'delete_tag_id',
    'get_operator',
    'post_itinerary_template',
    'put_itinerary_template_id',
    'get_itinerary_template',
    'get_itinerary_template_id',
    'get_event_definition_category',
    'post_event_definition_category',
    'delete_event_definition_category_id',
    'put_event_definition_category_id',
    'post_badge',
    'put_badge_id',
    'get_badge',
    'get_badge_id',
    'get_badge_id_history',
    'AccessibleClientsPayload',
    'AccessibleClientsResponseItem',
    'ChangeClientPayload',
    'ChangeClientResponse',
    'ChangelogResponse',
    'ClientResponse',
    'CurrentUserResponse',
    'DeleteContainerIdBody',
    'DeleteRoundIdRoundBody',
    'GetDepotsResponseItem',
    'GetOutletsResponseItem',
    'GetPoisResponseItem',
    'GetPoisResponseItemPlace',
    'GetPoisResponseItemPoiDefinition',
    'ItineraryCreationData',
    'PoiRoutePart',
    'PoiRoutePartProducingPlace',
    'PoiRoutePartState',
    'PoiRoutePartType',
    'PostAdministrativeGroupIdHistoryExportBody',
    'PostAttachmentBody',
    'PostBadgeBody',
    'PostCommentBody',
    'PostContainerDeleteManyBody',
    'PostContainerManyBody',
    'PostContainerRealisedBody',
    'PostCustomFieldBody',
    'PostDeviceLiveDataUpdateBody',
    'PostDeviceSubmitCheckInBody',
    'PostDeviceUninavVersionBody',
    'PostEventDefinitionBody',
    'PostEventDefinitionCategoryBody',
    'PostExternalCreateIFMItineraryIdRealisationBody',
    'PostExternalLiveVehicleDataBody',
    'PostInterventionMoveBody',
    'PostItineraryTemplateBody',
    'PostLogisticAdministrativeGroupExportBillingBody',
    'PostMapCorrectionBody',
    'PostOperationalLayersDataSourceBody',
    'PostOutletRealisedBody',
    'PostPoiDefinitionBody',
    'PostProducerDeleteManyBody',
    'PostProducingPlaceBySerialNumbersBody',
    'PostProducingPlaceCollectablesBatchBody',
    'PostProducingPlaceCollectablesBody',
    'PostProducingPlaceDeleteManyBody',
    'PostProducingPlaceIdCollectionPlanningBody',
    'PostProducingPlaceManyBody',
    'PostProducingPlaceUniqueStreamContainersTotalByIdsBody',
    'PostRealisationDeleteManyBody',
    'PostRotationHistoryBody',
    'PostRoundTracksBody',
    'PostRoutePartAvailabilitiesBody',
    'PostRoutePartEventInPolygonBody',
    'PostRoutePartProducingPlaceInPolygonBody',
    'PostRoutePartSegmentInLineBody',
    'PostRoutePartSegmentInPolygonBody',
    'PostSectorBody',
    'PostStreamBody',
    'PostStreetServiceTransposeBody',
    'PostUniAndCoUserBody',
    'PostUserBody',
    'PostUserEventDefinitionEmailSubscriptionBody',
    'PostUserRoleBody',
    'PostVehicleLoadingTypeBody',
    'PostVehicleProfileBody',
    'PostWasteBatchBody',
    'PutAttachmentIdBody',
    'PutAuthResetPasswordBody',
    'PutAuthUpdatePasswordBody',
    'PutBadgeIdBody',
    'PutCommentIdBody',
    'PutContainerIdBody',
    'PutContainerRealisedIdBody',
    'PutDepotIdPlaceBody',
    'PutDeviceClientBody',
    'PutEmployeeArchiveManyBody',
    'PutEmployeeIdBody',
    'PutEmployeeIdConstraintBody',
    'PutEventDefinitionCategoryIdBody',
    'PutEventDefinitionIdBody',
    'PutInterventionIdPlannedDateBody',
    'PutItineraryTemplateIdBody',
    'PutMapCommentBody',
    'PutOccurrenceItineraryBody',
    'PutOutletIdBody',
    'PutPlaceIdBody',
    'PutPoiDefinitionIdBody',
    'PutProducingPlaceConstraintBody',
    'PutProducingPlaceIdPlaceBody',
    'PutProducingPlaceIdStatusBody',
    'PutProducingPlaceLinkedProducersBody',
    'PutProducingPlaceRealisedIdBody',
    'PutRoundBody',
    'PutRoundRoundSlotsIdRoundBody',
    'PutRoutePartMoveManyBody',
    'PutStreamIdBody',
    'PutTagIdBody',
    'PutUserIdBody',
    'PutUserPreferencesLogisticParamsColumnBody',
    'PutUserPreferencesOperationalTabsParamsBody',
    'PutUserPreferencesPdfExportParamsBody',
    'PutUserRoleIdBody',
    'RegisterDevicePayload',
    'RegisterDeviceResponse',
    'RoundCreationData',
    'RoundCreationDataType',
    'RoundSlotData',
    'RoundSlotDataRecurrenceType',
    'SegmentRoutePart',
    'SegmentRoutePartDirection',
    'SegmentRoutePartInterventionMode',
    'SegmentRoutePartSide',
    'SegmentRoutePartState',
    'SegmentRoutePartType',
    'TokenPayload',
    'TokenResponse',
    'Client',
]
