from typing import TYPE_CHECKING, List, Optional

from ...models import GroupInfo, GroupListResponse, IdListResponse

if TYPE_CHECKING:
    from .. import API


class Group:
    def __init__(self, api: "API"):
        self._api = api

    def get(self, gids: str = "") -> List[GroupInfo]:
        """获取分组"""
        ret = self._api.call(GroupListResponse, self._api._payload.device_group_get, gids)
        if not (ret.status == 200 and ret.data.code == 0):
            return []
        return ret.data.group_list or []


    def set(self, gid: str, name: str) -> Optional[GroupInfo]:
        """设置分组"""
        ret = self._api.call(GroupListResponse, self._api._payload.device_group_set, gid, name)
        if ret.status == 200 and ret.data.code == 0:
            if len(ret.data.group_list) == 0:
                return None
            return ret.data.group_list[0]
        return None

    def add(self, name: str) -> Optional[GroupInfo]:
        """新增分组"""
        return self.set("0", name)

    def delete(self, gids: str) -> Optional[List[str]]:
        """删除分组"""
        ret = self._api.call(IdListResponse, self._api._payload.device_group_del, gids)
        if not (ret.status == 200 and ret.data.code == 0):
            return []
        result_list = ret.data.id_list if ret.data and ret.data.id_list else []
        return result_list
