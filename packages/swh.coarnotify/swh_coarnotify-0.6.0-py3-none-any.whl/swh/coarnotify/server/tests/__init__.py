# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
import uuid


def notification(
    id: str | uuid.UUID = "00000000-0000-0000-0000-000000000000",
    origin_url: str = "https://github.com/rdicosmo/parmap",
) -> dict:
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net",
        ],
        "actor": {
            "id": "https://research-organisation.org",
            "name": "Research Organisation",
            "type": "Organization",
        },
        "context": {
            "id": "https://research-organisation.org/paper123",
            "ietf:cite-as": "https://doi.org/10.5555/999555666",
            "ietf:item": {
                "id": "https://research-organisation.org/paper123/document.pdf",  # noqa: B950
                "mediaType": "application/pdf",
                "type": ["Object", "sorg:ScholarlyArticle"],
            },
            "type": ["Page", "sorg:AboutPage"],
        },
        "id": f"urn:uuid:{id}",
        "object": {
            "as:object": f"{origin_url}",
            "as:relationship": "https://w3id.org/codemeta/3.0#citation",
            "as:subject": "https://research-organisation.org/paper123",
            "id": "urn:uuid:74FFB356-0632-44D9-B176-888DA85758DC",
            "type": "Relationship",
        },
        "origin": {
            "id": "https://research-organisation.org/repository",
            "inbox": "http://inbox.partner.local",
            "type": "Service",
        },
        "target": {
            "id": "https://swh",
            "inbox": "http://testserver/",
            "type": "Service",
        },
        "type": ["Announce", "coar-notify:RelationshipAction"],
    }
