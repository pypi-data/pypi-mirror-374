S_RES_PARTNER_GET = {"_id": {"type": "integer"}}

S_RES_PARTNER_RETURN_GET = {
    "id": {"type": "integer", "required": True},
    "name": {"type": "string", "required": True},
    "email": {"type": "string", "required": True},
    "is_subscriber": {"type": "boolean", "required": True},
}
