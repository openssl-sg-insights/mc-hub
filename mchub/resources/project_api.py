from flask import request
from sqlalchemy import inspect

from .api_view import ApiView
from ..database import db
from ..models.user import User, UserORM
from ..models.cloud.project import Project, Provider, ENV_VALIDATORS
from ..exceptions.invalid_usage_exception import (
    InvalidUsageException,
)


class ProjectAPI(ApiView):
    def get(self, user: User):
        if len(user.projects) > 0:
            return [
                {
                    "id": project.id,
                    "name": project.name,
                    "provider": project.provider,
                    "nb_clusters": len(project.magic_castles),
                    "admin": project.admin_id == user.orm.id,
                }
                for project in user.projects
            ]
        return []

    def post(self, user: User):
        data = request.get_json()
        if not data:
            raise InvalidUsageException("No json data was provided")
        try:
            provider = Provider(data["provider"])
            env = data["env"]
            name = data["name"]
        except KeyError as err:
            raise InvalidUsageException(f"Missing required field {err}")

        try:
            env = ENV_VALIDATORS[provider](env)
        except Exception as err:
            raise InvalidUsageException("Missing required environment variables")

        if user.orm.id is None:
            db.session.add(user.orm)
            db.session.commit()

        project = Project(name=name, admin_id=user.orm.id, provider=provider, env=env)
        user.orm.projects.append(project)
        db.session.add(project)
        db.session.commit()
        return {
            "id": project.id,
            "name": project.name,
            "provider": project.provider,
            "nb_clusters": len(project.magic_castles),
            "admin": project.admin_id == user.orm.id,
        }, 200

    def patch(self, user: User, id: int):
        project = Project.query.get(id)
        if project is None or project not in user.orm.projects:
            raise InvalidUsageException("Invalid project id")
        if project.admin_id != user.orm.id:
            raise InvalidUsageException(
                "Cannot edit project membership that you are not the admin of"
            )
        data = request.get_json()
        if not data:
            raise InvalidUsageException("No json data was provided")

        add_members = data.get("add", [])
        del_members = data.get("del", [])

        for username in add_members:
            member = UserORM.query.filter_by(scoped_id=username).first()
            if not member:
                member = UserORM(scoped_id=username)
                db.session.add(member)
            member.projects.append(project)

        for username in del_members:
            member = UserORM.query.filter_by(scoped_id=username).first()
            if member and member.id != user.orm.id:
                member.projects.remove(project)

        db.session.commit()

    def delete(self, user: User, id: int):
        project = Project.query.get(id)
        if project is None or project not in user.orm.projects:
            raise InvalidUsageException("Invalid project id")
        if project.admin_id != user.orm.id:
            raise InvalidUsageException(
                "Cannot remove project that you are not the admin of"
            )
        if len(project.magic_castles) > 0:
            raise InvalidUsageException("Cannot remove project with running clusters")
        user.orm.projects.remove(project)
        db.session.delete(project)
        db.session.commit()
        return "", 200
