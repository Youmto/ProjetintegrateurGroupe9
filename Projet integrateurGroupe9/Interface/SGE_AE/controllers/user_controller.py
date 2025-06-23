from models.user_model import list_users, list_roles, assign_role, revoke_role

def get_all_users(conn):
    return list_users(conn)

def get_all_roles(conn):
    return list_roles(conn)

def activate_user_role(conn, user_id, role_id):
    assign_role(conn, user_id, role_id)

def deactivate_user_role(conn, user_id, role_id):
    revoke_role(conn, user_id, role_id)