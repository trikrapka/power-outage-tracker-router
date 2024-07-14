from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session, InstrumentedAttribute
from database import User, Identifier, OutageData


class UserManager:
    def __init__(self, session: Session):
        self.session = session
        self.power_outage_starts: Dict[str, Dict[str, Dict[str, Optional[datetime]]]] = {}

    def add_user(self, chat_id: str) -> None:
        if not self.session.query(User).filter_by(chat_id=chat_id).first():
            new_user = User(chat_id=chat_id)
            self.session.add(new_user)
            self.session.commit()
            self.power_outage_starts[chat_id] = {'urls': {}, 'ips': {}}

    def add_identifier(self, chat_id: str, identifier: str, identifier_type: str) -> bool:
        user = self.session.query(User).filter_by(chat_id=chat_id).first()
        if not user:
            self.add_user(chat_id)
            user = self.session.query(User).filter_by(chat_id=chat_id).first()

        existing_identifier = self.session.query(Identifier).filter_by(
            user_id=user.id, identifier=identifier, identifier_type=identifier_type
        ).first()

        if not existing_identifier:
            new_identifier = Identifier(user_id=user.id, identifier=identifier, identifier_type=identifier_type)
            self.session.add(new_identifier)
            self.session.commit()
            if chat_id not in self.power_outage_starts:
                self.power_outage_starts[chat_id] = {'urls': {}, 'ips': {}}
            self.power_outage_starts[chat_id][identifier_type][identifier] = None
            return True
        return False

    def delete_identifier(self, chat_id: str, identifier: str, identifier_type: str) -> bool:
        user = self.session.query(User).filter_by(chat_id=chat_id).first()
        if user:
            identifier_obj = self.session.query(Identifier).filter_by(
                user_id=user.id, identifier=identifier, identifier_type=identifier_type
            ).first()
            if identifier_obj:
                self.session.delete(identifier_obj)
                self.session.commit()
                if chat_id in self.power_outage_starts and identifier_type in self.power_outage_starts[chat_id]:
                    self.power_outage_starts[chat_id][identifier_type].pop(identifier, None)
                return True
        return False

    def get_identifiers(self, chat_id: str, identifier_type: str) -> list[InstrumentedAttribute] | list[Any]:
        user = self.session.query(User).filter_by(chat_id=chat_id).first()
        if user:
            identifiers = self.session.query(Identifier).filter_by(
                user_id=user.id, identifier_type=identifier_type
            ).all()
            return [identifier.identifier for identifier in identifiers]
        return []

    def get_power_outage_start(self, chat_id: str, identifier: str, identifier_type: str) -> Optional[datetime]:
        return self.power_outage_starts.get(chat_id, {}).get(identifier_type, {}).get(identifier)

    def set_power_outage_start(self, chat_id: str, identifier: str, identifier_type: str, time: Optional[datetime]) -> None:
        if chat_id not in self.power_outage_starts:
            self.power_outage_starts[chat_id] = {'urls': {}, 'ips': {}}
        self.power_outage_starts[chat_id][identifier_type][identifier] = time

    def save_outage_data(self, chat_id: str, identifier: str, identifier_type: str, start_time: datetime, end_time: datetime) -> None:
        user = self.session.query(User).filter_by(chat_id=chat_id).first()
        if user:
            outage_data = OutageData(
                user_id=user.id,
                identifier=identifier,
                identifier_type=identifier_type,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds()
            )
            self.session.add(outage_data)
            self.session.commit()

    def generate_weekly_report(self, chat_id: str) -> Dict[str, Dict[str, Any]]:
        user = self.session.query(User).filter_by(chat_id=chat_id).first()
        if not user:
            return {}

        current_time = datetime.now()
        one_week_ago = current_time - timedelta(days=7)
        report = {}

        outage_data = self.session.query(OutageData).filter(
            OutageData.user_id == user.id,
            OutageData.start_time >= one_week_ago
        ).all()

        for entry in outage_data:
            identifier = entry.identifier
            if identifier not in report:
                report[identifier] = {
                    "shutdown_count": 0,
                    "total_duration": timedelta(),
                    "longest_shutdown": timedelta(),
                    "shortest_shutdown": timedelta(days=7),
                }

            duration = timedelta(seconds=entry.duration_seconds)
            report[identifier]["shutdown_count"] += 1
            report[identifier]["total_duration"] += duration
            report[identifier]["longest_shutdown"] = max(report[identifier]["longest_shutdown"], duration)
            report[identifier]["shortest_shutdown"] = min(report[identifier]["shortest_shutdown"], duration)

        for identifier, data in report.items():
            if data["shutdown_count"] > 0:
                data["average_shutdown_length"] = data["total_duration"] / data["shutdown_count"]
            else:
                data["average_shutdown_length"] = timedelta()

            if data["shortest_shutdown"] == timedelta(days=7):
                data["shortest_shutdown"] = timedelta()

        return report