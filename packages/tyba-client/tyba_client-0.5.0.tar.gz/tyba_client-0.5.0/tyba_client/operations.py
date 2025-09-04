import datetime
import json
from datetime import date
from typing import Optional, Literal


class ValidationError(ValueError):
    pass


class Operations(object):
    def __init__(self, client):
        self.client = client

    def get(self, route, params=None):
        response = self.client.get(f"operations/{route}", params=params)
        response.raise_for_status()
        return response.text


    def post(self, route, json):
        return self.client.post(f"operations/{route}", json=json)

    def performance_report(
            self,
            start_date: date,
            end_date: date,
            asset_name: str | None,
            display_name: str | None = None
    ):
        if not (asset_name or display_name):
            raise ValidationError("Must provide either 'asset_name' or 'display_name'.")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        if asset_name:
            params["asset_name"] = asset_name
        else:
            params["asset_display_name"] = display_name

        return self.get("internal_api/performance_report", params=params)

    def da_snapshot(
            self,
            start_date: date,
            end_date: date,
            asset_name: str | None,
            display_name: str | None = None
    ):
        if not (asset_name or display_name):
            raise ValidationError("Must provide either 'asset_name' or 'display_name'.")
        params= {
            "start_date": start_date,
            "end_date": end_date,
        }
        if asset_name:
            params["asset_name"] = asset_name
        else:
            params["asset_display_name"] = display_name


        return self.get(
            "internal_api/da_snapshot",
            params=params,
        )

    def telemetry(
            self,
            start_date: date,
            end_date: date,
            asset_name: str | None,
            interval_mins: int,
            metrics: list[str],
            solar_asset_telemetry: bool = False,
            display_name: str | None = None
    ):
        if not (asset_name or display_name):
            raise ValidationError("Must provide either 'asset_name' or 'display_name'.")
        params= {
                "start_date": start_date,
                "end_date": end_date,
                "interval_mins": interval_mins,
                "metrics": metrics,
                "solar_asset_telemetry": solar_asset_telemetry,
            }
        if asset_name:
            params["asset_name"] = asset_name
        else:
            params["asset_display_name"] = display_name

        return self.get(
                "internal_api/telemetry",
                params=params,
            )

    def asset_details(
            self,
            asset_name: str | None,
            date: Optional[datetime.date] = None,
            display_name: str | None = None
    ):
        if not (asset_name or display_name):
            raise ValidationError("Must provide either 'asset_name' or 'display_name'.")
        params= {}
        if asset_name:
            params["asset_name"] = asset_name
        else:
            params["asset_display_name"] = display_name

        if date is not None:
            params["date"] = date
        return self.get("internal_api/asset_details", params=params)

    def assets(
            self,
            org_id: Optional[str] = None,
            include_disabled: bool = False,
    ):
        params = {"include_disabled": include_disabled}
        if org_id:
            params["org_id"] = org_id
        return self.get("internal_api/assets", params=params)

    def set_asset_overrides(
            self,
            asset_names: list[str],
            field: str,
            aggregation: Literal["global", "single_day", "single_day_hourly", "12x24"],
            values,
            service: Optional[str] = None,
            date: Optional[datetime.date] = None,
    ):
        assumption =  {
          "field": field,
         "data": {"aggregation":aggregation }
        }
        match aggregation:
            case "12x24":
                assumption["data"] = {"aggregation": "12x24"} | values
            case "single_day_hourly":
                assumption["data"] = {
                    "aggregation": "single_day_hourly",
                    "date": date,
                    "values": values
                }
            case "single_day":
                assumption["data"] = {
                    "aggregation": "single_day",
                    "values": values,
                    "date": date
                }
            case "global":
                assumption["data"] = {
                    "aggregation": "global",
                    "value": values
                }
        if service:
            assumption["service"] = service
        request_data = {"asset_names": asset_names, "assumption": assumption}

        res = self.post("internal_api/assets/override/", json=request_data)
        if res.status_code != 200:
            return {
                "status_code": res.status_code,
                "reason": res.reason,
                "message": res.text
            }
        else:
            return json.loads(res.text)



    def overrides_schema(
            self,
    ):

        return json.loads(self.get("internal_api/overrides_schema"))
