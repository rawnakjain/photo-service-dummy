import os
import logging
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, TEXT

from utils.normalizers import normalize_service_name

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        # Initialize MongoDB connection
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        database_name = os.getenv("MONGODB_DATABASE", "test")  # Using test database from the dump

        self.use_mock = False
        self.mock_services = []
        self.mock_salon_services = []
        self.mock_salon_service_variations = []
        self.mock_variation_name_service_id = []

        try:
            self.client: MongoClient = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Trigger a command to check the connection
            self.client.admin.command('ping')
            self.db = self.client[database_name]

            # Collection references
            self.services_collection = self.db.services
            self.salon_services_collection = self.db.salonservices
            self.salon_service_variations_collection = self.db.salonservicevariations
            self.variation_name_service_id_collection = self.db.variationnameandserviceid

            logger.info(f"Connected to MongoDB: {mongodb_uri}/{database_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB at {mongodb_uri}: {str(e)}. Using mock data.")
            self.use_mock = True
            self._load_mock_data()

    def _load_mock_data(self):
        """Load mock data for development and testing."""
        logger.info("Loading mock data for database service")

        # Mock services data
        self.mock_services = [
            {
                "_id": "mock_service_id_1",
                "serviceId": "904427b9-891f-42aa-9cf3-e596cfa4ce54",
                "serviceNameEnum": "makeup",
                "name": {"M": "Makeup", "F": "Makeup", "U": "Makeup"},
                "popularityIndex": 2900,
            },
            {
                "_id": "mock_service_id_2",
                "serviceId": "4e7fbd03-415c-4d1b-aa96-ec360f39ff8d",
                "serviceNameEnum": "basic_cleanup_facial",
                "name": {"M": "Basic Cleanup Facial", "F": "Basic Cleanup Facial", "U": "Basic Cleanup Facial"},
                "popularityIndex": 1500,
            },
            {
                "_id": "mock_service_id_3",
                "serviceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                "serviceNameEnum": "blow_dry",
                "name": {"M": "Blow Dry", "F": "Blow Dry", "U": "Blow Dry"},
                "popularityIndex": 1800,
            }
        ]

        # Mock salon services data (linking salon to services)
        self.mock_salon_services = [
            {
                "_id": "mock_salon_service_id_1",
                "salonServiceId": "283c2b74-fee9-4673-93df-f8bf593ae8da",
                "salonId": "2ef2d413-5a91-4318-a4fb-82dba24575db",
                "serviceId": "4e7fbd03-415c-4d1b-aa96-ec360f39ff8d",
                "serviceNameEnum": "basic_cleanup_facial",
                "salonServiceName": "Clean Up",
                "forGender": "F",
                "popularityIndex": 1,
            },
            {
                "_id": "mock_salon_service_id_2",
                "salonServiceId": "68f08d54-f667-44c9-84d2-e54803774b58",
                "salonId": "2ef2d413-5a91-4318-a4fb-82dba24575db",
                "serviceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                "serviceNameEnum": "blow_dry",
                "salonServiceName": "Blow Dry",
                "forGender": "F",
                "popularityIndex": 2,
            }
        ]

        # Mock salon service variations data
        self.mock_salon_service_variations = [
            {
                "_id": "mock_variation_id_1",
                "salonServiceVariationId": "b2d43171-e929-4fb8-829d-b70f37a14bf9",
                "salonServiceId": "283c2b74-fee9-4673-93df-f8bf593ae8da",
                "serviceId": "4e7fbd03-415c-4d1b-aa96-ec360f39ff8d",
                "salonId": "2ef2d413-5a91-4318-a4fb-82dba24575db",
                "fullName": "Clean Up O3+",
                "salonServiceName": "Clean Up",
                "serviceName": "Basic Cleanup Facial",
                "price": 1000,
                "originalPrice": 1200,
                "duration": 45,
                "bufferInMins": 5,
                "pricingType": "FIXED",
                "forGender": "F",
                "personType": "A",
                "genericService": "Y",
                "isCombo": False,
                "tagNameAndValues": [{"tagNameEnum": "brandType", "tagValueEnum": "o3Plus"}],
                "categoryLabel": "salon",
                "vatCategory": "",
                "pricePerUnit": 0,
                "unitType": "",
                "basePriceCalculationType": "FLAT"
            },
            {
                "_id": "mock_variation_id_2",
                "salonServiceVariationId": "706eb579-466c-400f-a856-42a4dfc4010a",
                "salonServiceId": "e604eb53-ccf7-4090-bd94-594aae5a1a6c",
                "serviceId": "30947532-9a60-435f-809c-2ce163534ed3",
                "salonId": "2ef2d413-5a91-4318-a4fb-82dba24575db",
                "fullName": "Head Massage",
                "salonServiceName": "Massage",
                "serviceName": "Massage",
                "price": 400,
                "originalPrice": 500,
                "duration": 20,
                "bufferInMins": 5,
                "pricingType": "FIXED",
                "forGender": "F",
                "personType": "A",
                "genericService": "Y",
                "isCombo": False,
                "tagNameAndValues": [
                    {"tagNameEnum": "areaCoverage", "tagValueEnum": "head"},
                    {"tagNameEnum": "additionalFeature", "tagValueEnum": "withoutWash"}
                ],
                "categoryLabel": "salon",
                "vatCategory": "",
                "pricePerUnit": 0,
                "unitType": "",
                "basePriceCalculationType": "FLAT"
            },
            {
                "_id": "mock_variation_id_3",
                "salonServiceVariationId": "6234eb02-0457-40b1-8b5d-fbba0bf98429",
                "salonServiceId": "68f08d54-f667-44c9-84d2-e54803774b58",
                "serviceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                "salonId": "2ef2d413-5a91-4318-a4fb-82dba24575db",
                "fullName": "Hair Cut + Hair Wash + Blow Dryer, With Style Director",
                "salonServiceName": "Blow Dry",
                "serviceName": "Blow Dry",
                "price": 1500,
                "originalPrice": 1800,
                "duration": 60,
                "bufferInMins": 5,
                "pricingType": "FIXED",
                "forGender": "F",
                "personType": "A",
                "genericService": "Y",
                "isCombo": True,
                "tagNameAndValues": [
                    {"tagNameEnum": "serviceType", "tagValueEnum": "styleDirector"},
                    {"tagNameEnum": "combo", "tagValueEnum": "hairCutHairWashBlowDry"}
                ],
                "categoryLabel": "salon",
                "vatCategory": "",
                "pricePerUnit": 0,
                "unitType": "",
                "basePriceCalculationType": "FLAT"
            }
        ]

        # Mock variation name and service id data (for text search)
        self.mock_variation_name_service_id = [
            {
                "_id": "mock_vns_id_1",
                "serviceId": "4e7fbd03-415c-4d1b-aa96-ec360f39ff8d",
                "variationId": "b2d43171-e929-4fb8-829d-b70f37a14bf9",
                "variationName": "Clean Up O3+"
            },
            {
                "_id": "mock_vns_id_2",
                "serviceId": "30947532-9a60-435f-809c-2ce163534ed3",
                "variationId": "706eb579-466c-400f-a856-42a4dfc4010a",
                "variationName": "Head Massage"
            },
            {
                "_id": "mock_vns_id_3",
                "serviceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                "variationId": "6234eb02-0457-40b1-8b5d-fbba0bf98429",
                "variationName": "Hair Cut + Hair Wash + Blow Dryer, With Style Director"
            }
        ]

    def find_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a service by name in the services collection.

        Args:
            service_name: Name of the service to search for

        Returns:
            Service document if found, None otherwise
        """
        try:
            if self.use_mock:
                # Mock implementation
                normalized_name = normalize_service_name(service_name)
                for service in self.mock_services:
                    if normalize_service_name(service.get("serviceNameEnum", "")) == normalized_name:
                        return service
                    # Also check partial match
                    if normalized_name in normalize_service_name(service.get("serviceNameEnum", "")):
                        return service
                return None
            else:
                # Real MongoDB implementation
                normalized_name = normalize_service_name(service_name)

                # Try exact match first
                service = self.services_collection.find_one({
                    "serviceNameEnum": {"$regex": f"^{re.escape(normalized_name)}$", "$options": "i"}
                })

                if service:
                    logger.debug(f"Found exact service match for '{service_name}': {service.get('serviceId')}")
                    return service

                # Try case-insensitive partial match
                service = self.services_collection.find_one({
                    "serviceNameEnum": {"$regex": normalized_name, "$options": "i"}
                })

                if service:
                    logger.debug(f"Found partial service match for '{service_name}': {service.get('serviceId')}")
                    return service

                return None

        except Exception as e:
            logger.error(f"Error finding service by name '{service_name}': {str(e)}")
            if self.use_mock:
                return None
            # In case of real DB error, we could fall back to mock, but for now just return None
            return None

    def find_variations_for_service(
        self,
        service_id: str,
        salon_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all variations for a given service, optionally filtered by salon.

        Args:
            service_id: The service ID to find variations for
            salon_id: Optional salon ID to filter by

        Returns:
            List of variation documents
        """
        try:
            if self.use_mock:
                # Mock implementation
                variations = []
                for variation in self.mock_salon_service_variations:
                    if variation.get("serviceId") == service_id:
                        if salon_id is None or variation.get("salonId") == salon_id:
                            variations.append(variation)
                logger.debug(f"Found {len(variations)} variations for service {service_id}" +
                            (f" in salon {salon_id}" if salon_id else ""))
                return variations
            else:
                # Real MongoDB implementation
                query = {"serviceId": service_id}

                if salon_id:
                    query["salonId"] = salon_id

                variations = list(self.salon_service_variations_collection.find(query))

                logger.debug(f"Found {len(variations)} variations for service {service_id}" +
                            (f" in salon {salon_id}" if salon_id else ""))

                return variations

        except Exception as e:
            logger.error(f"Error finding variations for service {service_id}: {str(e)}")
            return []

    def search_variations_by_name(
        self,
        variation_name: str,
        salon_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for variations by name using the variationnameandserviceid collection.

        Args:
            variation_name: Name of the variation to search for
            salon_id: Optional salon ID to filter by

        Returns:
            List of variation documents (from salonServiceVariations collection)
        """
        try:
            if self.use_mock:
                # Mock implementation
                normalized_name = normalize_service_name(variation_name)
                variation_ids = []
                service_ids = set()
                for item in self.mock_variation_name_service_id:
                    if normalized_name in normalize_service_name(item.get("variationName", "")):
                        variation_ids.append(item.get("variationId"))
                        service_ids.add(item.get("serviceId"))

                # Now fetch the actual variations from salonServiceVariations
                variations = []
                for variation in self.mock_salon_service_variations:
                    if variation.get("salonServiceVariationId") in variation_ids:
                        if salon_id is None or variation.get("salonId") == salon_id:
                            variations.append(variation)

                logger.debug(f"Found {len(variations)} variations via name search for '{variation_name}'")
                return variations
            else:
                # Real MongoDB implementation
                # Normalize the search term
                normalized_name = normalize_service_name(variation_name)

                # Search in the variation name index
                query = {
                    "variationName": {"$regex": normalized_name, "$options": "i"}
                }

                # Get matching variation IDs
                variation_matches = list(self.variation_name_service_id_collection.find(
                    query,
                    {"variationId": 1, "serviceId": 1}
                ))

                if not variation_matches:
                    logger.debug(f"No variation name matches found for '{variation_name}'")
                    return []

                # Extract unique variation IDs and service IDs
                variation_ids = list(set(match["variationId"] for match in variation_matches))
                service_ids = list(set(match["serviceId"] for match in variation_matches))

                # Now fetch the actual variations from salonServiceVariations
                variation_query = {"salonServiceVariationId": {"$in": variation_ids}}
                if salon_id:
                    variation_query["salonId"] = salon_id

                variations = list(self.salon_service_variations_collection.find(
                    variation_query
                ))

                logger.debug(f"Found {len(variations)} variations via name search for '{variation_name}'")
                return variations

        except Exception as e:
            logger.error(f"Error searching variations by name '{variation_name}': {str(e)}")
            return []

    def close(self):
        """Close the MongoDB connection."""
        if not self.use_mock and self.client:
            self.client.close()
            logger.info("MongoDB connection closed")