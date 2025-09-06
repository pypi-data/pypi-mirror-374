#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = ["Client", "CLOUDDRIVE_API_MAP"]

from collections.abc import Coroutine
from functools import cached_property
from typing import overload, Any, Iterable, Literal, Never, Sequence
from urllib.parse import urlsplit, urlunsplit

from google.protobuf.empty_pb2 import Empty # type: ignore
from google.protobuf.json_format import ParseDict # type: ignore
from google.protobuf.message import Message # type: ignore
from grpc import insecure_channel, Channel # type: ignore
from grpclib.client import Channel as AsyncChannel # type: ignore
from yarl import URL

import pathlib, sys
PROTO_DIR = str(pathlib.Path(__file__).parent / "proto")
if PROTO_DIR not in sys.path:
    sys.path.append(PROTO_DIR)

import clouddrive.pb2
from .proto import CloudDrive_grpc, CloudDrive_pb2_grpc


CLOUDDRIVE_API_MAP = {
    "APIAddLocalFolder": {"argument": dict | clouddrive.pb2.AddLocalFolderRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILogin115Editthiscookie": {"argument": dict | clouddrive.pb2.Login115EditthiscookieRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILogin115OpenOAuth": {"argument": dict | clouddrive.pb2.Login115OpenOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILogin115OpenQRCode": {"return": Iterable[clouddrive.pb2.QRCodeScanMessage]}, 
    "APILogin115QRCode": {"argument": dict | clouddrive.pb2.Login115QrCodeRequest, "return": Iterable[clouddrive.pb2.QRCodeScanMessage]}, 
    "APILogin189QRCode": {"return": Iterable[clouddrive.pb2.QRCodeScanMessage]}, 
    "APILoginAliyunDriveQRCode": {"argument": dict | clouddrive.pb2.LoginAliyundriveQRCodeRequest, "return": Iterable[clouddrive.pb2.QRCodeScanMessage]}, 
    "APILoginAliyundriveOAuth": {"argument": dict | clouddrive.pb2.LoginAliyundriveOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILoginAliyundriveRefreshtoken": {"argument": dict | clouddrive.pb2.LoginAliyundriveRefreshtokenRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILoginBaiduPanOAuth": {"argument": dict | clouddrive.pb2.LoginBaiduPanOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILoginCloudDrive": {"argument": dict | clouddrive.pb2.LoginCloudDriveRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILoginOneDriveOAuth": {"argument": dict | clouddrive.pb2.LoginOneDriveOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "APILoginWebDav": {"argument": dict | clouddrive.pb2.LoginWebDavRequest, "return": clouddrive.pb2.APILoginResult}, 
    "ActivatePlan": {"argument": dict | clouddrive.pb2.StringValue, "return": clouddrive.pb2.JoinPlanResult}, 
    "AddDavUser": {"argument": dict | clouddrive.pb2.AddDavUserRequest}, 
    "AddMountPoint": {"argument": dict | clouddrive.pb2.MountOption, "return": clouddrive.pb2.MountPointResult}, 
    "AddOfflineFiles": {"argument": dict | clouddrive.pb2.AddOfflineFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "AddSharedLink": {"argument": dict | clouddrive.pb2.AddSharedLinkRequest}, 
    "AddWebhookConfig": {"argument": dict | clouddrive.pb2.WebhookRequest}, 
    "ApiLogin123panOAuth": {"argument": dict | clouddrive.pb2.Login123panOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "ApiLoginGoogleDriveOAuth": {"argument": dict | clouddrive.pb2.LoginGoogleDriveOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "ApiLoginGoogleDriveRefreshToken": {"argument": dict | clouddrive.pb2.LoginGoogleDriveRefreshTokenRequest, "return": clouddrive.pb2.APILoginResult}, 
    "ApiLoginXunleiOAuth": {"argument": dict | clouddrive.pb2.LoginXunleiOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "ApiLoginXunleiOpenOAuth": {"argument": dict | clouddrive.pb2.LoginXunleiOpenOAuthRequest, "return": clouddrive.pb2.APILoginResult}, 
    "BackupAdd": {"argument": dict | clouddrive.pb2.Backup}, 
    "BackupAddDestination": {"argument": dict | clouddrive.pb2.BackupModifyRequest}, 
    "BackupGetAll": {"return": clouddrive.pb2.BackupList}, 
    "BackupGetStatus": {"argument": dict | clouddrive.pb2.StringValue, "return": clouddrive.pb2.BackupStatus}, 
    "BackupRemove": {"argument": dict | clouddrive.pb2.StringValue}, 
    "BackupRemoveDestination": {"argument": dict | clouddrive.pb2.BackupModifyRequest}, 
    "BackupRestartWalkingThrough": {"argument": dict | clouddrive.pb2.StringValue}, 
    "BackupSetEnabled": {"argument": dict | clouddrive.pb2.BackupSetEnabledRequest}, 
    "BackupSetFileSystemWatchEnabled": {"argument": dict | clouddrive.pb2.BackupModifyRequest}, 
    "BackupUpdate": {"argument": dict | clouddrive.pb2.Backup}, 
    "BackupUpdateStrategies": {"argument": dict | clouddrive.pb2.BackupModifyRequest}, 
    "BindCloudAccount": {"argument": dict | clouddrive.pb2.BindCloudAccountRequest}, 
    "CanAddMoreBackups": {"return": clouddrive.pb2.FileOperationResult}, 
    "CanAddMoreCloudApis": {"return": clouddrive.pb2.FileOperationResult}, 
    "CanAddMoreMountPoints": {"return": clouddrive.pb2.FileOperationResult}, 
    "CanMountBothLocalAndCloud": {"return": clouddrive.pb2.BoolResult}, 
    "CancelAllUploadFiles": {}, 
    "CancelCopyTask": {"argument": dict | clouddrive.pb2.CopyTaskRequest}, 
    "CancelMergeTask": {"argument": dict | clouddrive.pb2.CancelMergeTaskRequest}, 
    "CancelUploadFiles": {"argument": dict | clouddrive.pb2.MultpleUploadFileKeyRequest}, 
    "ChangeEmail": {"argument": dict | clouddrive.pb2.ChangeEmailRequest}, 
    "ChangeEmailAndPassword": {"argument": dict | clouddrive.pb2.ChangeEmailAndPasswordRequest}, 
    "ChangePassword": {"argument": dict | clouddrive.pb2.ChangePasswordRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "ChangeWebhookConfig": {"argument": dict | clouddrive.pb2.WebhookRequest}, 
    "CheckActivationCode": {"argument": dict | clouddrive.pb2.StringValue, "return": clouddrive.pb2.CheckActivationCodeResult}, 
    "CheckCouponCode": {"argument": dict | clouddrive.pb2.CheckCouponCodeRequest, "return": clouddrive.pb2.CouponCodeResult}, 
    "CheckUpdate": {"return": clouddrive.pb2.UpdateResult}, 
    "ClearOfflineFiles": {"argument": dict | clouddrive.pb2.ClearOfflineFileRequest}, 
    "CloseFile": {"argument": dict | clouddrive.pb2.CloseFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "ConfirmEmail": {"argument": dict | clouddrive.pb2.ConfirmEmailRequest}, 
    "CopyFile": {"argument": dict | clouddrive.pb2.CopyFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "CreateEncryptedFolder": {"argument": dict | clouddrive.pb2.CreateEncryptedFolderRequest, "return": clouddrive.pb2.CreateFolderResult}, 
    "CreateFile": {"argument": dict | clouddrive.pb2.CreateFileRequest, "return": clouddrive.pb2.CreateFileResult}, 
    "CreateFolder": {"argument": dict | clouddrive.pb2.CreateFolderRequest, "return": clouddrive.pb2.CreateFolderResult}, 
    "CreateToken": {"argument": dict | clouddrive.pb2.CreateTokenRequest, "return": clouddrive.pb2.TokenInfo}, 
    "DeleteFile": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "DeleteFilePermanently": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "DeleteFiles": {"argument": dict | clouddrive.pb2.MultiFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "DeleteFilesPermanently": {"argument": dict | clouddrive.pb2.MultiFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "DownloadUpdate": {}, 
    "FindFileByPath": {"argument": dict | clouddrive.pb2.FindFileByPathRequest, "return": clouddrive.pb2.CloudDriveFile}, 
    "ForceExpireDirCache": {"argument": dict | clouddrive.pb2.FileRequest}, 
    "GetAccountStatus": {"return": clouddrive.pb2.AccountStatusResult}, 
    "GetAllCloudApis": {"return": clouddrive.pb2.CloudAPIList}, 
    "GetAllTasksCount": {"return": clouddrive.pb2.GetAllTasksCountResult}, 
    "GetApiTokenInfo": {"argument": dict | clouddrive.pb2.StringValue, "return": clouddrive.pb2.TokenInfo}, 
    "GetAvailableDriveLetters": {"return": clouddrive.pb2.GetAvailableDriveLettersResult}, 
    "GetBalanceLog": {"return": clouddrive.pb2.BalanceLogResult}, 
    "GetCloudAPIConfig": {"argument": dict | clouddrive.pb2.GetCloudAPIConfigRequest, "return": clouddrive.pb2.CloudAPIConfig}, 
    "GetCloudDrive1UserData": {"return": clouddrive.pb2.StringResult}, 
    "GetCloudDrivePlans": {"return": clouddrive.pb2.GetCloudDrivePlansResult}, 
    "GetCloudMemberships": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.CloudMemberships}, 
    "GetCopyTasks": {"return": clouddrive.pb2.GetCopyTaskResult}, 
    "GetDavServerConfig": {"return": clouddrive.pb2.DavServerConfig}, 
    "GetDavUser": {"argument": dict | clouddrive.pb2.StringValue, "return": clouddrive.pb2.DavUser}, 
    "GetDirCacheTable": {"return": clouddrive.pb2.DirCacheTable}, 
    "GetDownloadFileCount": {"return": clouddrive.pb2.GetDownloadFileCountResult}, 
    "GetDownloadFileList": {"return": clouddrive.pb2.GetDownloadFileListResult}, 
    "GetDownloadUrlPath": {"argument": dict | clouddrive.pb2.GetDownloadUrlPathRequest, "return": clouddrive.pb2.DownloadUrlPathInfo}, 
    "GetEffectiveDirCacheTimeSecs": {"argument": dict | clouddrive.pb2.GetEffectiveDirCacheTimeRequest, "return": clouddrive.pb2.GetEffectiveDirCacheTimeResult}, 
    "GetFileDetailProperties": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileDetailProperties}, 
    "GetMachineId": {"return": clouddrive.pb2.StringResult}, 
    "GetMergeTasks": {"return": clouddrive.pb2.GetMergeTasksResult}, 
    "GetMetaData": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileMetaData}, 
    "GetMountPoints": {"return": clouddrive.pb2.GetMountPointsResult}, 
    "GetOfflineQuotaInfo": {"argument": dict | clouddrive.pb2.OfflineQuotaRequest, "return": clouddrive.pb2.OfflineQuotaInfo}, 
    "GetOnlineDevices": {"return": clouddrive.pb2.OnlineDevices}, 
    "GetOpenFileHandles": {"return": clouddrive.pb2.OpenFileHandleList}, 
    "GetOpenFileTable": {"argument": dict | clouddrive.pb2.GetOpenFileTableRequest, "return": clouddrive.pb2.OpenFileTable}, 
    "GetOriginalPath": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.StringResult}, 
    "GetPromotions": {"return": clouddrive.pb2.GetPromotionsResult}, 
    "GetPromotionsByCloud": {"argument": dict | clouddrive.pb2.CloudAPIRequest, "return": clouddrive.pb2.GetPromotionsResult}, 
    "GetReferencedEntryPaths": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.StringList}, 
    "GetReferralCode": {"return": clouddrive.pb2.StringValue}, 
    "GetRunningInfo": {"return": clouddrive.pb2.RunInfo}, 
    "GetRuntimeInfo": {"return": clouddrive.pb2.RuntimeInfo}, 
    "GetSearchResults": {"argument": dict | clouddrive.pb2.SearchRequest, "return": Iterable[clouddrive.pb2.SubFilesReply]}, 
    "GetSpaceInfo": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.SpaceInfo}, 
    "GetSubFiles": {"argument": dict | clouddrive.pb2.ListSubFileRequest, "return": Iterable[clouddrive.pb2.SubFilesReply]}, 
    "GetSystemInfo": {"return": clouddrive.pb2.CloudDriveSystemInfo}, 
    "GetSystemSettings": {"return": clouddrive.pb2.SystemSettings}, 
    "GetTempFileTable": {"return": clouddrive.pb2.TempFileTable}, 
    "GetToken": {"argument": dict | clouddrive.pb2.GetTokenRequest, "return": clouddrive.pb2.JWTToken}, 
    "GetUploadFileCount": {"return": clouddrive.pb2.GetUploadFileCountResult}, 
    "GetUploadFileList": {"argument": dict | clouddrive.pb2.GetUploadFileListRequest, "return": clouddrive.pb2.GetUploadFileListResult}, 
    "GetWebhookConfigTemplate": {"return": clouddrive.pb2.StringResult}, 
    "GetWebhookConfigs": {"return": clouddrive.pb2.WebhookList}, 
    "HasDriveLetters": {"return": clouddrive.pb2.HasDriveLettersResult}, 
    "HasUpdate": {"return": clouddrive.pb2.UpdateResult}, 
    "JoinPlan": {"argument": dict | clouddrive.pb2.JoinPlanRequest, "return": clouddrive.pb2.JoinPlanResult}, 
    "KickoutDevice": {"argument": dict | clouddrive.pb2.DeviceRequest}, 
    "ListAllOfflineFiles": {"argument": dict | clouddrive.pb2.OfflineFileListAllRequest, "return": clouddrive.pb2.OfflineFileListAllResult}, 
    "ListLogFiles": {"return": clouddrive.pb2.ListLogFileResult}, 
    "ListOfflineFilesByPath": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.OfflineFileListResult}, 
    "ListTokens": {"return": clouddrive.pb2.ListTokensResult}, 
    "LocalGetSubFiles": {"argument": dict | clouddrive.pb2.LocalGetSubFilesRequest, "return": Iterable[clouddrive.pb2.LocalGetSubFilesResult]}, 
    "LockEncryptedFile": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "Login": {"argument": dict | clouddrive.pb2.UserLoginRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "Logout": {"argument": dict | clouddrive.pb2.UserLogoutRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "ModifyDavUser": {"argument": dict | clouddrive.pb2.ModifyDavUserRequest}, 
    "ModifyToken": {"argument": dict | clouddrive.pb2.ModifyTokenRequest, "return": clouddrive.pb2.TokenInfo}, 
    "Mount": {"argument": dict | clouddrive.pb2.MountPointRequest, "return": clouddrive.pb2.MountPointResult}, 
    "MoveFile": {"argument": dict | clouddrive.pb2.MoveFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "PauseAllCopyTasks": {"argument": dict | clouddrive.pb2.PauseAllCopyTasksRequest, "return": clouddrive.pb2.BatchOperationResult}, 
    "PauseAllUploadFiles": {}, 
    "PauseCopyTask": {"argument": dict | clouddrive.pb2.PauseCopyTaskRequest}, 
    "PauseCopyTasks": {"argument": dict | clouddrive.pb2.PauseCopyTasksRequest, "return": clouddrive.pb2.BatchOperationResult}, 
    "PauseUploadFiles": {"argument": dict | clouddrive.pb2.MultpleUploadFileKeyRequest}, 
    "PushMessage": {"return": Iterable[clouddrive.pb2.CloudDrivePushMessage]}, 
    "PushTaskChange": {"return": Iterable[clouddrive.pb2.GetAllTasksCountResult]}, 
    "Register": {"argument": dict | clouddrive.pb2.UserRegisterRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "RemoteUploadStream": {"argument": Sequence[dict | clouddrive.pb2.RemoteEntryRequest], "return": Iterable[clouddrive.pb2.RemoteEntryResponse]}, 
    "RemoveAllCopyTasks": {"return": clouddrive.pb2.BatchOperationResult}, 
    "RemoveCloudAPI": {"argument": dict | clouddrive.pb2.RemoveCloudAPIRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "RemoveCompletedCopyTasks": {}, 
    "RemoveCopyTasks": {"argument": dict | clouddrive.pb2.CopyTaskBatchRequest, "return": clouddrive.pb2.BatchOperationResult}, 
    "RemoveDavUser": {"argument": dict | clouddrive.pb2.StringValue}, 
    "RemoveMountPoint": {"argument": dict | clouddrive.pb2.MountPointRequest, "return": clouddrive.pb2.MountPointResult}, 
    "RemoveOfflineFiles": {"argument": dict | clouddrive.pb2.RemoveOfflineFilesRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "RemoveToken": {"argument": dict | clouddrive.pb2.StringValue}, 
    "RemoveWebhookConfig": {"argument": dict | clouddrive.pb2.StringValue}, 
    "RenameFile": {"argument": dict | clouddrive.pb2.RenameFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "RenameFiles": {"argument": dict | clouddrive.pb2.RenameFilesRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "ResetAccount": {"argument": dict | clouddrive.pb2.ResetAccountRequest}, 
    "RestartCopyTask": {"argument": dict | clouddrive.pb2.CopyTaskRequest}, 
    "RestartOfflineTask": {"argument": dict | clouddrive.pb2.RestartOfflineFileRequest}, 
    "RestartService": {}, 
    "ResumeAllCopyTasks": {"return": clouddrive.pb2.BatchOperationResult}, 
    "ResumeAllUploadFiles": {}, 
    "ResumeCopyTasks": {"argument": dict | clouddrive.pb2.CopyTaskBatchRequest, "return": clouddrive.pb2.BatchOperationResult}, 
    "ResumeUploadFiles": {"argument": dict | clouddrive.pb2.MultpleUploadFileKeyRequest}, 
    "SendChangeEmailCode": {"argument": dict | clouddrive.pb2.SendChangeEmailCodeRequest}, 
    "SendConfirmEmail": {}, 
    "SendPromotionAction": {"argument": dict | clouddrive.pb2.SendPromotionActionRequest}, 
    "SendResetAccountEmail": {"argument": dict | clouddrive.pb2.SendResetAccountEmailRequest}, 
    "SetCloudAPIConfig": {"argument": dict | clouddrive.pb2.SetCloudAPIConfigRequest}, 
    "SetDavServerConfig": {"argument": dict | clouddrive.pb2.ModifyDavServerConfigRequest}, 
    "SetDirCacheTimeSecs": {"argument": dict | clouddrive.pb2.SetDirCacheTimeRequest}, 
    "SetSystemSettings": {"argument": dict | clouddrive.pb2.SystemSettings}, 
    "ShutdownService": {}, 
    "StartCloudEventListener": {"argument": dict | clouddrive.pb2.FileRequest}, 
    "StopCloudEventListener": {"argument": dict | clouddrive.pb2.FileRequest}, 
    "SyncFileChangesFromCloud": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.FileSystemChangeStatistics}, 
    "TestUpdate": {"argument": dict | clouddrive.pb2.FileRequest}, 
    "TransferBalance": {"argument": dict | clouddrive.pb2.TransferBalanceRequest}, 
    "UnlockEncryptedFile": {"argument": dict | clouddrive.pb2.UnlockEncryptedFileRequest, "return": clouddrive.pb2.FileOperationResult}, 
    "Unmount": {"argument": dict | clouddrive.pb2.MountPointRequest, "return": clouddrive.pb2.MountPointResult}, 
    "UpdateMountPoint": {"argument": dict | clouddrive.pb2.UpdateMountPointRequest, "return": clouddrive.pb2.MountPointResult}, 
    "UpdatePromotionResult": {}, 
    "UpdatePromotionResultByCloud": {"argument": dict | clouddrive.pb2.UpdatePromotionResultByCloudRequest}, 
    "UpdateSystem": {}, 
    "WalkThroughFolderTest": {"argument": dict | clouddrive.pb2.FileRequest, "return": clouddrive.pb2.WalkThroughFolderResult}, 
    "WriteToFile": {"argument": dict | clouddrive.pb2.WriteFileRequest, "return": clouddrive.pb2.WriteFileResult}, 
    "WriteToFileStream": {"argument": Sequence[dict | clouddrive.pb2.WriteFileRequest], "return": clouddrive.pb2.WriteFileResult}, 
}


def to_message(cls, o, /) -> Message:
    if isinstance(o, Message):
        return o
    elif type(o) is dict:
        return ParseDict(o, cls())
    elif type(o) is tuple:
        return cls(**{f.name: a for f, a in zip(cls.DESCRIPTOR.fields, o)})
    else:
        return cls(**{cls.DESCRIPTOR.fields[0].name: o})


class Client:
    "clouddrive client that encapsulates grpc APIs"
    origin: URL
    username: str
    password: str
    token: str
    download_baseurl: str
    metadata: list[tuple[str, str]]

    def __init__(
        self, 
        /, 
        origin: str = "http://localhost:19798", 
        username: str = "", 
        password: str = "", 
        token: str = "",
    ):
        origin = origin.rstrip("/")
        urlp = urlsplit(origin)
        scheme = urlp.scheme or "http"
        netloc = urlp.netloc or "localhost:19798"
        self.__dict__.update(
            origin = URL(urlunsplit(urlp._replace(scheme=scheme, netloc=netloc))), 
            download_baseurl = f"{scheme}://{netloc}/static/{scheme}/{netloc}/False/", 
            username = username, 
            password = password, 
            metadata = [], 
        )
        if username:
            self.login()
        if token:
            self.metadata[:] = [("authorization", "Bearer " + token),]

    def __del__(self, /):
        self.close()

    def __eq__(self, other, /) -> bool:
        return type(self) is type(other) and self.origin == other.origin and self.username == other.username

    def __hash__(self, /) -> int:
        return hash((self.origin, self.username))

    def __repr__(self, /) -> str:
        cls = type(self)
        module = cls.__module__
        name = cls.__qualname__
        if module != "__main__":
            name = module + "." + name
        return f"{name}(origin={self.origin!r}, username={self.username!r}, password='******')"

    def __setattr__(self, attr, val, /) -> Never:
        raise TypeError("can't set attribute")

    @cached_property
    def channel(self, /) -> Channel:
        return insecure_channel(self.origin.authority)

    @cached_property
    def stub(self, /) -> clouddrive.proto.CloudDrive_pb2_grpc.CloudDriveFileSrvStub:
        return CloudDrive_pb2_grpc.CloudDriveFileSrvStub(self.channel)

    @cached_property
    def async_channel(self, /) -> AsyncChannel:
        origin = self.origin
        return AsyncChannel(origin.host, origin.port)

    @cached_property
    def async_stub(self, /) -> clouddrive.proto.CloudDrive_grpc.CloudDriveFileSrvStub:
        return CloudDrive_grpc.CloudDriveFileSrvStub(self.async_channel)

    def close(self, /):
        ns = self.__dict__
        if "channel" in ns:
            ns["channel"].close()
        if "async_channel" in ns:
            ns["async_channel"].close()

    def set_password(self, value: str, /):
        self.__dict__["password"] = value
        self.login()

    def login(
        self, 
        /, 
        username: str = "", 
        password: str = "", 
    ):
        if not username:
            username = self.username
        if not password:
            password = self.password
        response = self.stub.GetToken(clouddrive.pb2.GetTokenRequest(userName=username, password=password))
        self.metadata[:] = [("authorization", "Bearer " + response.token),]

    @overload
    def APIAddLocalFolder(
        self, 
        arg: dict | clouddrive.pb2.AddLocalFolderRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APIAddLocalFolder(
        self, 
        arg: dict | clouddrive.pb2.AddLocalFolderRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APIAddLocalFolder(
        self, 
        arg: dict | clouddrive.pb2.AddLocalFolderRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APIAddLocalFolder(AddLocalFolderRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message AddLocalFolderRequest {
          string localFolderPath = 1;
        }
        """
        arg = to_message(clouddrive.pb2.AddLocalFolderRequest, arg)
        if async_:
            return self.async_stub.APIAddLocalFolder(arg, metadata=self.metadata)
        else:
            return self.stub.APIAddLocalFolder(arg, metadata=self.metadata)

    @overload
    def APILogin115Editthiscookie(
        self, 
        arg: dict | clouddrive.pb2.Login115EditthiscookieRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILogin115Editthiscookie(
        self, 
        arg: dict | clouddrive.pb2.Login115EditthiscookieRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILogin115Editthiscookie(
        self, 
        arg: dict | clouddrive.pb2.Login115EditthiscookieRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILogin115Editthiscookie(Login115EditthiscookieRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message Login115EditthiscookieRequest {
          string editThiscookieString = 1;
        }
        """
        arg = to_message(clouddrive.pb2.Login115EditthiscookieRequest, arg)
        if async_:
            return self.async_stub.APILogin115Editthiscookie(arg, metadata=self.metadata)
        else:
            return self.stub.APILogin115Editthiscookie(arg, metadata=self.metadata)

    @overload
    def APILogin115OpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login115OpenOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILogin115OpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login115OpenOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILogin115OpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login115OpenOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILogin115OpenOAuth(Login115OpenOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message Login115OpenOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.Login115OpenOAuthRequest, arg)
        if async_:
            return self.async_stub.APILogin115OpenOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.APILogin115OpenOAuth(arg, metadata=self.metadata)

    @overload
    def APILogin115OpenQRCode(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage]:
        ...
    @overload
    def APILogin115OpenQRCode(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        ...
    def APILogin115OpenQRCode(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage] | Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILogin115OpenQRCode(google.protobuf.Empty) returns (stream QRCodeScanMessage);

        ------------------- protobuf type definition -------------------

        message QRCodeScanMessage {
          QRCodeScanMessageType messageType = 1;
          string message = 2;
        }
        enum QRCodeScanMessageType {
          QRCodeScanMessageType_SHOW_IMAGE = 0;
          QRCodeScanMessageType_SHOW_IMAGE_CONTENT = 1;
          QRCodeScanMessageType_CHANGE_STATUS = 2;
          QRCodeScanMessageType_CLOSE = 3;
          QRCodeScanMessageType_ERROR = 4;
        }
        """
        if async_:
            return self.async_stub.APILogin115OpenQRCode(Empty(), metadata=self.metadata)
        else:
            return self.stub.APILogin115OpenQRCode(Empty(), metadata=self.metadata)

    @overload
    def APILogin115QRCode(
        self, 
        arg: dict | clouddrive.pb2.Login115QrCodeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage]:
        ...
    @overload
    def APILogin115QRCode(
        self, 
        arg: dict | clouddrive.pb2.Login115QrCodeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        ...
    def APILogin115QRCode(
        self, 
        arg: dict | clouddrive.pb2.Login115QrCodeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage] | Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILogin115QRCode(Login115QrCodeRequest) returns (stream QRCodeScanMessage);

        ------------------- protobuf type definition -------------------

        message Login115QrCodeRequest {
          string platformString = 1;
        }
        message QRCodeScanMessage {
          QRCodeScanMessageType messageType = 1;
          string message = 2;
        }
        enum QRCodeScanMessageType {
          QRCodeScanMessageType_SHOW_IMAGE = 0;
          QRCodeScanMessageType_SHOW_IMAGE_CONTENT = 1;
          QRCodeScanMessageType_CHANGE_STATUS = 2;
          QRCodeScanMessageType_CLOSE = 3;
          QRCodeScanMessageType_ERROR = 4;
        }
        """
        arg = to_message(clouddrive.pb2.Login115QrCodeRequest, arg)
        if async_:
            return self.async_stub.APILogin115QRCode(arg, metadata=self.metadata)
        else:
            return self.stub.APILogin115QRCode(arg, metadata=self.metadata)

    @overload
    def APILogin189QRCode(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage]:
        ...
    @overload
    def APILogin189QRCode(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        ...
    def APILogin189QRCode(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage] | Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILogin189QRCode(google.protobuf.Empty) returns (stream QRCodeScanMessage);

        ------------------- protobuf type definition -------------------

        message QRCodeScanMessage {
          QRCodeScanMessageType messageType = 1;
          string message = 2;
        }
        enum QRCodeScanMessageType {
          QRCodeScanMessageType_SHOW_IMAGE = 0;
          QRCodeScanMessageType_SHOW_IMAGE_CONTENT = 1;
          QRCodeScanMessageType_CHANGE_STATUS = 2;
          QRCodeScanMessageType_CLOSE = 3;
          QRCodeScanMessageType_ERROR = 4;
        }
        """
        if async_:
            return self.async_stub.APILogin189QRCode(Empty(), metadata=self.metadata)
        else:
            return self.stub.APILogin189QRCode(Empty(), metadata=self.metadata)

    @overload
    def APILoginAliyunDriveQRCode(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveQRCodeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage]:
        ...
    @overload
    def APILoginAliyunDriveQRCode(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveQRCodeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        ...
    def APILoginAliyunDriveQRCode(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveQRCodeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.QRCodeScanMessage] | Coroutine[Any, Any, Iterable[clouddrive.pb2.QRCodeScanMessage]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginAliyunDriveQRCode(LoginAliyundriveQRCodeRequest) returns (stream QRCodeScanMessage);

        ------------------- protobuf type definition -------------------

        message LoginAliyundriveQRCodeRequest {
          bool useOpenAPI = 1;
        }
        message QRCodeScanMessage {
          QRCodeScanMessageType messageType = 1;
          string message = 2;
        }
        enum QRCodeScanMessageType {
          QRCodeScanMessageType_SHOW_IMAGE = 0;
          QRCodeScanMessageType_SHOW_IMAGE_CONTENT = 1;
          QRCodeScanMessageType_CHANGE_STATUS = 2;
          QRCodeScanMessageType_CLOSE = 3;
          QRCodeScanMessageType_ERROR = 4;
        }
        """
        arg = to_message(clouddrive.pb2.LoginAliyundriveQRCodeRequest, arg)
        if async_:
            return self.async_stub.APILoginAliyunDriveQRCode(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginAliyunDriveQRCode(arg, metadata=self.metadata)

    @overload
    def APILoginAliyundriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginAliyundriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginAliyundriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginAliyundriveOAuth(LoginAliyundriveOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginAliyundriveOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginAliyundriveOAuthRequest, arg)
        if async_:
            return self.async_stub.APILoginAliyundriveOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginAliyundriveOAuth(arg, metadata=self.metadata)

    @overload
    def APILoginAliyundriveRefreshtoken(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveRefreshtokenRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginAliyundriveRefreshtoken(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveRefreshtokenRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginAliyundriveRefreshtoken(
        self, 
        arg: dict | clouddrive.pb2.LoginAliyundriveRefreshtokenRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginAliyundriveRefreshtoken(LoginAliyundriveRefreshtokenRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginAliyundriveRefreshtokenRequest {
          string refreshToken = 1;
          bool useOpenAPI = 2;
        }
        """
        arg = to_message(clouddrive.pb2.LoginAliyundriveRefreshtokenRequest, arg)
        if async_:
            return self.async_stub.APILoginAliyundriveRefreshtoken(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginAliyundriveRefreshtoken(arg, metadata=self.metadata)

    @overload
    def APILoginBaiduPanOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginBaiduPanOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginBaiduPanOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginBaiduPanOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginBaiduPanOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginBaiduPanOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginBaiduPanOAuth(LoginBaiduPanOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginBaiduPanOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginBaiduPanOAuthRequest, arg)
        if async_:
            return self.async_stub.APILoginBaiduPanOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginBaiduPanOAuth(arg, metadata=self.metadata)

    @overload
    def APILoginCloudDrive(
        self, 
        arg: dict | clouddrive.pb2.LoginCloudDriveRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginCloudDrive(
        self, 
        arg: dict | clouddrive.pb2.LoginCloudDriveRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginCloudDrive(
        self, 
        arg: dict | clouddrive.pb2.LoginCloudDriveRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginCloudDrive(LoginCloudDriveRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginCloudDriveRequest {
          string grpcUrl = 1;
          string token = 2;
          bool insecureTls = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginCloudDriveRequest, arg)
        if async_:
            return self.async_stub.APILoginCloudDrive(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginCloudDrive(arg, metadata=self.metadata)

    @overload
    def APILoginOneDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginOneDriveOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginOneDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginOneDriveOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginOneDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginOneDriveOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginOneDriveOAuth(LoginOneDriveOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginOneDriveOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginOneDriveOAuthRequest, arg)
        if async_:
            return self.async_stub.APILoginOneDriveOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginOneDriveOAuth(arg, metadata=self.metadata)

    @overload
    def APILoginWebDav(
        self, 
        arg: dict | clouddrive.pb2.LoginWebDavRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def APILoginWebDav(
        self, 
        arg: dict | clouddrive.pb2.LoginWebDavRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def APILoginWebDav(
        self, 
        arg: dict | clouddrive.pb2.LoginWebDavRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc APILoginWebDav(LoginWebDavRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginWebDavRequest {
          string serverUrl = 1;
          string userName = 2;
          string password = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginWebDavRequest, arg)
        if async_:
            return self.async_stub.APILoginWebDav(arg, metadata=self.metadata)
        else:
            return self.stub.APILoginWebDav(arg, metadata=self.metadata)

    @overload
    def ActivatePlan(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.JoinPlanResult:
        ...
    @overload
    def ActivatePlan(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.JoinPlanResult]:
        ...
    def ActivatePlan(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.JoinPlanResult | Coroutine[Any, Any, clouddrive.pb2.JoinPlanResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ActivatePlan(StringValue) returns (JoinPlanResult);

        ------------------- protobuf type definition -------------------

        message JoinPlanResult {
          bool success = 1;
          double balance = 2;
          string planName = 3;
          string planDescription = 4;
          google.protobuf.Timestamp expireTime = 5;
          PaymentInfo paymentInfo = 6;
        }
        message PaymentInfo {
          string user_id = 1;
          string plan_id = 2;
          map<string, string> paymentMethods = 3;
          string coupon_code = 4;
          string machine_id = 5;
          string check_code = 6;
        }
        message StringValue {
          string value = 1;
        }
        """
        arg = to_message(clouddrive.pb2.StringValue, arg)
        if async_:
            return self.async_stub.ActivatePlan(arg, metadata=self.metadata)
        else:
            return self.stub.ActivatePlan(arg, metadata=self.metadata)

    @overload
    def AddDavUser(
        self, 
        arg: dict | clouddrive.pb2.AddDavUserRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def AddDavUser(
        self, 
        arg: dict | clouddrive.pb2.AddDavUserRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def AddDavUser(
        self, 
        arg: dict | clouddrive.pb2.AddDavUserRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc AddDavUser(AddDavUserRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message AddDavUserRequest {
          string userName = 1;
          string password = 2;
          string rootPath = 3;
          bool readOnly = 4;
          bool enabled = 5;
          bool guest = 6;
        }
        """
        if async_:
            async def request():
                await self.async_stub.AddDavUser(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.AddDavUser(arg, metadata=self.metadata)
            return None

    @overload
    def AddMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountOption, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.MountPointResult:
        ...
    @overload
    def AddMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountOption, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        ...
    def AddMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountOption, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.MountPointResult | Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc AddMountPoint(MountOption) returns (MountPointResult);

        ------------------- protobuf type definition -------------------

        message MountOption {
          string mountPoint = 1;
          string sourceDir = 2;
          bool localMount = 3;
          bool readOnly = 4;
          bool autoMount = 5;
          uint32 uid = 6;
          uint32 gid = 7;
          string permissions = 8;
          string name = 9;
        }
        message MountPointResult {
          bool success = 1;
          string failReason = 2;
        }
        """
        arg = to_message(clouddrive.pb2.MountOption, arg)
        if async_:
            return self.async_stub.AddMountPoint(arg, metadata=self.metadata)
        else:
            return self.stub.AddMountPoint(arg, metadata=self.metadata)

    @overload
    def AddOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.AddOfflineFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def AddOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.AddOfflineFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def AddOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.AddOfflineFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc AddOfflineFiles(AddOfflineFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message AddOfflineFileRequest {
          string urls = 1;
          string toFolder = 2;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.AddOfflineFileRequest, arg)
        if async_:
            return self.async_stub.AddOfflineFiles(arg, metadata=self.metadata)
        else:
            return self.stub.AddOfflineFiles(arg, metadata=self.metadata)

    @overload
    def AddSharedLink(
        self, 
        arg: dict | clouddrive.pb2.AddSharedLinkRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def AddSharedLink(
        self, 
        arg: dict | clouddrive.pb2.AddSharedLinkRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def AddSharedLink(
        self, 
        arg: dict | clouddrive.pb2.AddSharedLinkRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc AddSharedLink(AddSharedLinkRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message AddSharedLinkRequest {
          string sharedLinkUrl = 1;
          string sharedPassword = 2;
          string toFolder = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.AddSharedLink(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.AddSharedLink(arg, metadata=self.metadata)
            return None

    @overload
    def AddWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def AddWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def AddWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc AddWebhookConfig(WebhookRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message WebhookRequest {
          string fileName = 1;
          string content = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.AddWebhookConfig(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.AddWebhookConfig(arg, metadata=self.metadata)
            return None

    @overload
    def ApiLogin123panOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login123panOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def ApiLogin123panOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login123panOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def ApiLogin123panOAuth(
        self, 
        arg: dict | clouddrive.pb2.Login123panOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ApiLogin123panOAuth(Login123panOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message Login123panOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.Login123panOAuthRequest, arg)
        if async_:
            return self.async_stub.ApiLogin123panOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.ApiLogin123panOAuth(arg, metadata=self.metadata)

    @overload
    def ApiLoginGoogleDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def ApiLoginGoogleDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def ApiLoginGoogleDriveOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ApiLoginGoogleDriveOAuth(LoginGoogleDriveOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginGoogleDriveOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginGoogleDriveOAuthRequest, arg)
        if async_:
            return self.async_stub.ApiLoginGoogleDriveOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.ApiLoginGoogleDriveOAuth(arg, metadata=self.metadata)

    @overload
    def ApiLoginGoogleDriveRefreshToken(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveRefreshTokenRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def ApiLoginGoogleDriveRefreshToken(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveRefreshTokenRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def ApiLoginGoogleDriveRefreshToken(
        self, 
        arg: dict | clouddrive.pb2.LoginGoogleDriveRefreshTokenRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ApiLoginGoogleDriveRefreshToken(LoginGoogleDriveRefreshTokenRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginGoogleDriveRefreshTokenRequest {
          string client_id = 1;
          string client_secret = 2;
          string refresh_token = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginGoogleDriveRefreshTokenRequest, arg)
        if async_:
            return self.async_stub.ApiLoginGoogleDriveRefreshToken(arg, metadata=self.metadata)
        else:
            return self.stub.ApiLoginGoogleDriveRefreshToken(arg, metadata=self.metadata)

    @overload
    def ApiLoginXunleiOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def ApiLoginXunleiOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def ApiLoginXunleiOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ApiLoginXunleiOAuth(LoginXunleiOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginXunleiOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginXunleiOAuthRequest, arg)
        if async_:
            return self.async_stub.ApiLoginXunleiOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.ApiLoginXunleiOAuth(arg, metadata=self.metadata)

    @overload
    def ApiLoginXunleiOpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOpenOAuthRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.APILoginResult:
        ...
    @overload
    def ApiLoginXunleiOpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOpenOAuthRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        ...
    def ApiLoginXunleiOpenOAuth(
        self, 
        arg: dict | clouddrive.pb2.LoginXunleiOpenOAuthRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.APILoginResult | Coroutine[Any, Any, clouddrive.pb2.APILoginResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ApiLoginXunleiOpenOAuth(LoginXunleiOpenOAuthRequest) returns (APILoginResult);

        ------------------- protobuf type definition -------------------

        message APILoginResult {
          bool success = 1;
          string errorMessage = 2;
        }
        message LoginXunleiOpenOAuthRequest {
          string refresh_token = 1;
          string access_token = 2;
          uint64 expires_in = 3;
        }
        """
        arg = to_message(clouddrive.pb2.LoginXunleiOpenOAuthRequest, arg)
        if async_:
            return self.async_stub.ApiLoginXunleiOpenOAuth(arg, metadata=self.metadata)
        else:
            return self.stub.ApiLoginXunleiOpenOAuth(arg, metadata=self.metadata)

    @overload
    def BackupAdd(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupAdd(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupAdd(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupAdd(Backup) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message Backup {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          FileCompletionRule fileCompletionRule = 13;
          bool isEnabled = 6;
          bool fileSystemWatchEnabled = 7;
          int64 walkingThroughIntervalSecs = 8;
          bool forceWalkingThroughOnStart = 9;
          repeated TimeSchedule timeSchedules = 10;
          bool isTimeSchedulesEnabled = 11;
        }
        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileCompletionRule {
          FileCompletionRule_None = 0;
          FileCompletionRule_DeleteSource = 1;
          FileCompletionRule_DeleteSourceAndEmptyFolder = 2;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        message TimeSchedule {
          bool isEnabled = 1;
          uint32 hour = 2;
          uint32 minute = 3;
          uint32 second = 4;
          DaysOfWeek daysOfWeek = 5;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupAdd(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupAdd(arg, metadata=self.metadata)
            return None

    @overload
    def BackupAddDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupAddDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupAddDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupAddDestination(BackupModifyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message BackupModifyRequest {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          bool fileSystemWatchEnabled = 6;
          int64 walkingThroughIntervalSecs = 7;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupAddDestination(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupAddDestination(arg, metadata=self.metadata)
            return None

    @overload
    def BackupGetAll(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BackupList:
        ...
    @overload
    def BackupGetAll(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BackupList]:
        ...
    def BackupGetAll(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BackupList | Coroutine[Any, Any, clouddrive.pb2.BackupList]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupGetAll(google.protobuf.Empty) returns (BackupList);

        ------------------- protobuf type definition -------------------

        message BackupList {
          repeated BackupStatus backups = 1;
        }
        message BackupStatus {
          Backup backup = 1;
          Status status = 2;
          string statusMessage = 3;
          FileWatchStatus watcherStatus = 4;
          string watcherStatusMessage = 5;
          repeated TaskError errors = 7;
        }
        """
        if async_:
            return self.async_stub.BackupGetAll(Empty(), metadata=self.metadata)
        else:
            return self.stub.BackupGetAll(Empty(), metadata=self.metadata)

    @overload
    def BackupGetStatus(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BackupStatus:
        ...
    @overload
    def BackupGetStatus(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BackupStatus]:
        ...
    def BackupGetStatus(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BackupStatus | Coroutine[Any, Any, clouddrive.pb2.BackupStatus]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupGetStatus(StringValue) returns (BackupStatus);

        ------------------- protobuf type definition -------------------

        message Backup {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          FileCompletionRule fileCompletionRule = 13;
          bool isEnabled = 6;
          bool fileSystemWatchEnabled = 7;
          int64 walkingThroughIntervalSecs = 8;
          bool forceWalkingThroughOnStart = 9;
          repeated TimeSchedule timeSchedules = 10;
          bool isTimeSchedulesEnabled = 11;
        }
        message BackupStatus {
          Backup backup = 1;
          Status status = 2;
          string statusMessage = 3;
          FileWatchStatus watcherStatus = 4;
          string watcherStatusMessage = 5;
          repeated TaskError errors = 7;
        }
        enum FileWatchStatus {
          FileWatchStatus_WatcherIdle = 0;
          FileWatchStatus_Watching = 1;
          FileWatchStatus_WatcherError = 2;
          FileWatchStatus_WatcherDisabled = 3;
        }
        enum Status {
          Status_Idle = 0;
          Status_WalkingThrough = 1;
          Status_Error = 2;
          Status_Disabled = 3;
          Status_Scanned = 4;
          Status_Finished = 5;
        }
        message StringValue {
          string value = 1;
        }
        message TaskError {
          google.protobuf.Timestamp time = 1;
          string message = 2;
        }
        """
        arg = to_message(clouddrive.pb2.StringValue, arg)
        if async_:
            return self.async_stub.BackupGetStatus(arg, metadata=self.metadata)
        else:
            return self.stub.BackupGetStatus(arg, metadata=self.metadata)

    @overload
    def BackupRemove(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupRemove(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupRemove(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupRemove(StringValue) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupRemove(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupRemove(arg, metadata=self.metadata)
            return None

    @overload
    def BackupRemoveDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupRemoveDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupRemoveDestination(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupRemoveDestination(BackupModifyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message BackupModifyRequest {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          bool fileSystemWatchEnabled = 6;
          int64 walkingThroughIntervalSecs = 7;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupRemoveDestination(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupRemoveDestination(arg, metadata=self.metadata)
            return None

    @overload
    def BackupRestartWalkingThrough(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupRestartWalkingThrough(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupRestartWalkingThrough(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupRestartWalkingThrough(StringValue) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupRestartWalkingThrough(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupRestartWalkingThrough(arg, metadata=self.metadata)
            return None

    @overload
    def BackupSetEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupSetEnabledRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupSetEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupSetEnabledRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupSetEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupSetEnabledRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupSetEnabled(BackupSetEnabledRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BackupSetEnabledRequest {
          string sourcePath = 1;
          bool isEnabled = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupSetEnabled(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupSetEnabled(arg, metadata=self.metadata)
            return None

    @overload
    def BackupSetFileSystemWatchEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupSetFileSystemWatchEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupSetFileSystemWatchEnabled(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupSetFileSystemWatchEnabled(BackupModifyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message BackupModifyRequest {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          bool fileSystemWatchEnabled = 6;
          int64 walkingThroughIntervalSecs = 7;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupSetFileSystemWatchEnabled(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupSetFileSystemWatchEnabled(arg, metadata=self.metadata)
            return None

    @overload
    def BackupUpdate(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupUpdate(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupUpdate(
        self, 
        arg: dict | clouddrive.pb2.Backup, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupUpdate(Backup) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message Backup {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          FileCompletionRule fileCompletionRule = 13;
          bool isEnabled = 6;
          bool fileSystemWatchEnabled = 7;
          int64 walkingThroughIntervalSecs = 8;
          bool forceWalkingThroughOnStart = 9;
          repeated TimeSchedule timeSchedules = 10;
          bool isTimeSchedulesEnabled = 11;
        }
        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileCompletionRule {
          FileCompletionRule_None = 0;
          FileCompletionRule_DeleteSource = 1;
          FileCompletionRule_DeleteSourceAndEmptyFolder = 2;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        message TimeSchedule {
          bool isEnabled = 1;
          uint32 hour = 2;
          uint32 minute = 3;
          uint32 second = 4;
          DaysOfWeek daysOfWeek = 5;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupUpdate(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupUpdate(arg, metadata=self.metadata)
            return None

    @overload
    def BackupUpdateStrategies(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BackupUpdateStrategies(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BackupUpdateStrategies(
        self, 
        arg: dict | clouddrive.pb2.BackupModifyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BackupUpdateStrategies(BackupModifyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BackupDestination {
          string destinationPath = 1;
          bool isEnabled = 2;
          google.protobuf.Timestamp lastFinishTime = 3;
        }
        message BackupModifyRequest {
          string sourcePath = 1;
          repeated BackupDestination destinations = 2;
          repeated FileBackupRule fileBackupRules = 3;
          FileReplaceRule fileReplaceRule = 4;
          FileDeleteRule fileDeleteRule = 5;
          bool fileSystemWatchEnabled = 6;
          int64 walkingThroughIntervalSecs = 7;
        }
        message FileBackupRule {
          string extensions = 1;
          string fileNames = 2;
          string regex = 3;
          uint64 minSize = 4;
          bool isEnabled = 100;
          bool isBlackList = 101;
          bool applyToFolder = 102;
          bool applyToFile = 103;
        }
        enum FileDeleteRule {
          FileDeleteRule_Delete = 0;
          FileDeleteRule_Recycle = 1;
          FileDeleteRule_Keep = 2;
          FileDeleteRule_MoveToVersionHistory = 3;
        }
        enum FileReplaceRule {
          FileReplaceRule_Skip = 0;
          FileReplaceRule_Overwrite = 1;
          FileReplaceRule_KeepHistoryVersion = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BackupUpdateStrategies(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BackupUpdateStrategies(arg, metadata=self.metadata)
            return None

    @overload
    def BindCloudAccount(
        self, 
        arg: dict | clouddrive.pb2.BindCloudAccountRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def BindCloudAccount(
        self, 
        arg: dict | clouddrive.pb2.BindCloudAccountRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def BindCloudAccount(
        self, 
        arg: dict | clouddrive.pb2.BindCloudAccountRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc BindCloudAccount(BindCloudAccountRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message BindCloudAccountRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.BindCloudAccount(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.BindCloudAccount(arg, metadata=self.metadata)
            return None

    @overload
    def CanAddMoreBackups(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def CanAddMoreBackups(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def CanAddMoreBackups(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CanAddMoreBackups(google.protobuf.Empty) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        if async_:
            return self.async_stub.CanAddMoreBackups(Empty(), metadata=self.metadata)
        else:
            return self.stub.CanAddMoreBackups(Empty(), metadata=self.metadata)

    @overload
    def CanAddMoreCloudApis(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def CanAddMoreCloudApis(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def CanAddMoreCloudApis(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CanAddMoreCloudApis(google.protobuf.Empty) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        if async_:
            return self.async_stub.CanAddMoreCloudApis(Empty(), metadata=self.metadata)
        else:
            return self.stub.CanAddMoreCloudApis(Empty(), metadata=self.metadata)

    @overload
    def CanAddMoreMountPoints(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def CanAddMoreMountPoints(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def CanAddMoreMountPoints(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CanAddMoreMountPoints(google.protobuf.Empty) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        if async_:
            return self.async_stub.CanAddMoreMountPoints(Empty(), metadata=self.metadata)
        else:
            return self.stub.CanAddMoreMountPoints(Empty(), metadata=self.metadata)

    @overload
    def CanMountBothLocalAndCloud(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BoolResult:
        ...
    @overload
    def CanMountBothLocalAndCloud(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BoolResult]:
        ...
    def CanMountBothLocalAndCloud(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BoolResult | Coroutine[Any, Any, clouddrive.pb2.BoolResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CanMountBothLocalAndCloud(google.protobuf.Empty) returns (BoolResult);

        ------------------- protobuf type definition -------------------

        message BoolResult {
          bool result = 1;
        }
        """
        if async_:
            return self.async_stub.CanMountBothLocalAndCloud(Empty(), metadata=self.metadata)
        else:
            return self.stub.CanMountBothLocalAndCloud(Empty(), metadata=self.metadata)

    @overload
    def CancelAllUploadFiles(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def CancelAllUploadFiles(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def CancelAllUploadFiles(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CancelAllUploadFiles(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.CancelAllUploadFiles(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.CancelAllUploadFiles(Empty(), metadata=self.metadata)
            return None

    @overload
    def CancelCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def CancelCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def CancelCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CancelCopyTask(CopyTaskRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message CopyTaskRequest {
          string sourcePath = 1;
          string destPath = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.CancelCopyTask(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.CancelCopyTask(arg, metadata=self.metadata)
            return None

    @overload
    def CancelMergeTask(
        self, 
        arg: dict | clouddrive.pb2.CancelMergeTaskRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def CancelMergeTask(
        self, 
        arg: dict | clouddrive.pb2.CancelMergeTaskRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def CancelMergeTask(
        self, 
        arg: dict | clouddrive.pb2.CancelMergeTaskRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CancelMergeTask(CancelMergeTaskRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message CancelMergeTaskRequest {
          string sourcePath = 1;
          string destPath = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.CancelMergeTask(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.CancelMergeTask(arg, metadata=self.metadata)
            return None

    @overload
    def CancelUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def CancelUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def CancelUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CancelUploadFiles(MultpleUploadFileKeyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message MultpleUploadFileKeyRequest {
          repeated string keys = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.CancelUploadFiles(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.CancelUploadFiles(arg, metadata=self.metadata)
            return None

    @overload
    def ChangeEmail(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ChangeEmail(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ChangeEmail(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ChangeEmail(ChangeEmailRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ChangeEmailRequest {
          string newEmail = 1;
          string password = 2;
          string changeCode = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ChangeEmail(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ChangeEmail(arg, metadata=self.metadata)
            return None

    @overload
    def ChangeEmailAndPassword(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailAndPasswordRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ChangeEmailAndPassword(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailAndPasswordRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ChangeEmailAndPassword(
        self, 
        arg: dict | clouddrive.pb2.ChangeEmailAndPasswordRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ChangeEmailAndPassword(ChangeEmailAndPasswordRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ChangeEmailAndPasswordRequest {
          string newEmail = 1;
          string newPassword = 2;
          bool syncUserDataWithCloud = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ChangeEmailAndPassword(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ChangeEmailAndPassword(arg, metadata=self.metadata)
            return None

    @overload
    def ChangePassword(
        self, 
        arg: dict | clouddrive.pb2.ChangePasswordRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def ChangePassword(
        self, 
        arg: dict | clouddrive.pb2.ChangePasswordRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def ChangePassword(
        self, 
        arg: dict | clouddrive.pb2.ChangePasswordRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ChangePassword(ChangePasswordRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message ChangePasswordRequest {
          string oldPassword = 1;
          string newPassword = 2;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.ChangePasswordRequest, arg)
        if async_:
            return self.async_stub.ChangePassword(arg, metadata=self.metadata)
        else:
            return self.stub.ChangePassword(arg, metadata=self.metadata)

    @overload
    def ChangeWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ChangeWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ChangeWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.WebhookRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ChangeWebhookConfig(WebhookRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message WebhookRequest {
          string fileName = 1;
          string content = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ChangeWebhookConfig(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ChangeWebhookConfig(arg, metadata=self.metadata)
            return None

    @overload
    def CheckActivationCode(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CheckActivationCodeResult:
        ...
    @overload
    def CheckActivationCode(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CheckActivationCodeResult]:
        ...
    def CheckActivationCode(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CheckActivationCodeResult | Coroutine[Any, Any, clouddrive.pb2.CheckActivationCodeResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CheckActivationCode(StringValue) returns (CheckActivationCodeResult);

        ------------------- protobuf type definition -------------------

        message CheckActivationCodeResult {
          string planId = 1;
          string planName = 2;
          string planDescription = 3;
        }
        message StringValue {
          string value = 1;
        }
        """
        arg = to_message(clouddrive.pb2.StringValue, arg)
        if async_:
            return self.async_stub.CheckActivationCode(arg, metadata=self.metadata)
        else:
            return self.stub.CheckActivationCode(arg, metadata=self.metadata)

    @overload
    def CheckCouponCode(
        self, 
        arg: dict | clouddrive.pb2.CheckCouponCodeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CouponCodeResult:
        ...
    @overload
    def CheckCouponCode(
        self, 
        arg: dict | clouddrive.pb2.CheckCouponCodeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CouponCodeResult]:
        ...
    def CheckCouponCode(
        self, 
        arg: dict | clouddrive.pb2.CheckCouponCodeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CouponCodeResult | Coroutine[Any, Any, clouddrive.pb2.CouponCodeResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CheckCouponCode(CheckCouponCodeRequest) returns (CouponCodeResult);

        ------------------- protobuf type definition -------------------

        message CheckCouponCodeRequest {
          string planId = 1;
          string couponCode = 2;
        }
        message CouponCodeResult {
          string couponCode = 1;
          string couponDescription = 2;
          bool isPercentage = 3;
          double couponDiscountAmount = 4;
        }
        """
        arg = to_message(clouddrive.pb2.CheckCouponCodeRequest, arg)
        if async_:
            return self.async_stub.CheckCouponCode(arg, metadata=self.metadata)
        else:
            return self.stub.CheckCouponCode(arg, metadata=self.metadata)

    @overload
    def CheckUpdate(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.UpdateResult:
        ...
    @overload
    def CheckUpdate(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.UpdateResult]:
        ...
    def CheckUpdate(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.UpdateResult | Coroutine[Any, Any, clouddrive.pb2.UpdateResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CheckUpdate(google.protobuf.Empty) returns (UpdateResult);

        ------------------- protobuf type definition -------------------

        message UpdateResult {
          bool hasUpdate = 1;
          string newVersion = 2;
          string description = 3;
        }
        """
        if async_:
            return self.async_stub.CheckUpdate(Empty(), metadata=self.metadata)
        else:
            return self.stub.CheckUpdate(Empty(), metadata=self.metadata)

    @overload
    def ClearOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.ClearOfflineFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ClearOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.ClearOfflineFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ClearOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.ClearOfflineFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ClearOfflineFiles(ClearOfflineFileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ClearOfflineFileRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          Filter filter = 3;
          bool deleteFiles = 4;
          string path = 5;
        }
        enum Filter {
          Filter_All = 0;
          Filter_Finished = 1;
          Filter_Error = 2;
          Filter_Downloading = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ClearOfflineFiles(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ClearOfflineFiles(arg, metadata=self.metadata)
            return None

    @overload
    def CloseFile(
        self, 
        arg: dict | clouddrive.pb2.CloseFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def CloseFile(
        self, 
        arg: dict | clouddrive.pb2.CloseFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def CloseFile(
        self, 
        arg: dict | clouddrive.pb2.CloseFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CloseFile(CloseFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message CloseFileRequest {
          uint64 fileHandle = 1;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.CloseFileRequest, arg)
        if async_:
            return self.async_stub.CloseFile(arg, metadata=self.metadata)
        else:
            return self.stub.CloseFile(arg, metadata=self.metadata)

    @overload
    def ConfirmEmail(
        self, 
        arg: dict | clouddrive.pb2.ConfirmEmailRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ConfirmEmail(
        self, 
        arg: dict | clouddrive.pb2.ConfirmEmailRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ConfirmEmail(
        self, 
        arg: dict | clouddrive.pb2.ConfirmEmailRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ConfirmEmail(ConfirmEmailRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ConfirmEmailRequest {
          string confirmCode = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ConfirmEmail(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ConfirmEmail(arg, metadata=self.metadata)
            return None

    @overload
    def CopyFile(
        self, 
        arg: dict | clouddrive.pb2.CopyFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def CopyFile(
        self, 
        arg: dict | clouddrive.pb2.CopyFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def CopyFile(
        self, 
        arg: dict | clouddrive.pb2.CopyFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CopyFile(CopyFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        enum ConflictPolicy {
          ConflictPolicy_Overwrite = 0;
          ConflictPolicy_Rename = 1;
          ConflictPolicy_Skip = 2;
        }
        message CopyFileRequest {
          repeated string theFilePaths = 1;
          string destPath = 2;
          ConflictPolicy conflictPolicy = 3;
          bool handleConflictRecursively = 5;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.CopyFileRequest, arg)
        if async_:
            return self.async_stub.CopyFile(arg, metadata=self.metadata)
        else:
            return self.stub.CopyFile(arg, metadata=self.metadata)

    @overload
    def CreateEncryptedFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateEncryptedFolderRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CreateFolderResult:
        ...
    @overload
    def CreateEncryptedFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateEncryptedFolderRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CreateFolderResult]:
        ...
    def CreateEncryptedFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateEncryptedFolderRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CreateFolderResult | Coroutine[Any, Any, clouddrive.pb2.CreateFolderResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CreateEncryptedFolder(CreateEncryptedFolderRequest) returns (CreateFolderResult);

        ------------------- protobuf type definition -------------------

        message CloudDriveFile {
          string id = 1;
          string name = 2;
          string fullPathName = 3;
          int64 size = 4;
          FileType fileType = 5;
          google.protobuf.Timestamp createTime = 6;
          google.protobuf.Timestamp writeTime = 7;
          google.protobuf.Timestamp accessTime = 8;
          CloudAPI CloudAPI = 9;
          string thumbnailUrl = 10;
          string previewUrl = 11;
          string originalPath = 14;
          bool isDirectory = 30;
          bool isRoot = 31;
          bool isCloudRoot = 32;
          bool isCloudDirectory = 33;
          bool isCloudFile = 34;
          bool isSearchResult = 35;
          bool isForbidden = 36;
          bool isLocal = 37;
          bool canMount = 60;
          bool canUnmount = 61;
          bool canDirectAccessThumbnailURL = 62;
          bool canSearch = 63;
          bool hasDetailProperties = 64;
          FileDetailProperties detailProperties = 65;
          bool canOfflineDownload = 66;
          bool canAddShareLink = 67;
          uint64 dirCacheTimeToLiveSecs = 68;
          bool canDeletePermanently = 69;
          map<uint32, string> fileHashes = 70;
          FileEncryptionType fileEncryptionType = 71;
          bool CanCreateEncryptedFolder = 72;
          bool CanLock = 73;
          bool CanSyncFileChangesFromCloud = 74;
          bool supportOfflineDownloadManagement = 75;
          DownloadUrlPathInfo downloadUrlPath = 76;
        }
        message CreateEncryptedFolderRequest {
          string parentPath = 1;
          string folderName = 2;
          string password = 3;
          bool savePassword = 4;
        }
        message CreateFolderResult {
          CloudDriveFile folderCreated = 1;
          FileOperationResult result = 2;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.CreateEncryptedFolderRequest, arg)
        if async_:
            return self.async_stub.CreateEncryptedFolder(arg, metadata=self.metadata)
        else:
            return self.stub.CreateEncryptedFolder(arg, metadata=self.metadata)

    @overload
    def CreateFile(
        self, 
        arg: dict | clouddrive.pb2.CreateFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CreateFileResult:
        ...
    @overload
    def CreateFile(
        self, 
        arg: dict | clouddrive.pb2.CreateFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CreateFileResult]:
        ...
    def CreateFile(
        self, 
        arg: dict | clouddrive.pb2.CreateFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CreateFileResult | Coroutine[Any, Any, clouddrive.pb2.CreateFileResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CreateFile(CreateFileRequest) returns (CreateFileResult);

        ------------------- protobuf type definition -------------------

        message CreateFileRequest {
          string parentPath = 1;
          string fileName = 2;
        }
        message CreateFileResult {
          uint64 fileHandle = 1;
        }
        """
        arg = to_message(clouddrive.pb2.CreateFileRequest, arg)
        if async_:
            return self.async_stub.CreateFile(arg, metadata=self.metadata)
        else:
            return self.stub.CreateFile(arg, metadata=self.metadata)

    @overload
    def CreateFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateFolderRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CreateFolderResult:
        ...
    @overload
    def CreateFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateFolderRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CreateFolderResult]:
        ...
    def CreateFolder(
        self, 
        arg: dict | clouddrive.pb2.CreateFolderRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CreateFolderResult | Coroutine[Any, Any, clouddrive.pb2.CreateFolderResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CreateFolder(CreateFolderRequest) returns (CreateFolderResult);

        ------------------- protobuf type definition -------------------

        message CloudDriveFile {
          string id = 1;
          string name = 2;
          string fullPathName = 3;
          int64 size = 4;
          FileType fileType = 5;
          google.protobuf.Timestamp createTime = 6;
          google.protobuf.Timestamp writeTime = 7;
          google.protobuf.Timestamp accessTime = 8;
          CloudAPI CloudAPI = 9;
          string thumbnailUrl = 10;
          string previewUrl = 11;
          string originalPath = 14;
          bool isDirectory = 30;
          bool isRoot = 31;
          bool isCloudRoot = 32;
          bool isCloudDirectory = 33;
          bool isCloudFile = 34;
          bool isSearchResult = 35;
          bool isForbidden = 36;
          bool isLocal = 37;
          bool canMount = 60;
          bool canUnmount = 61;
          bool canDirectAccessThumbnailURL = 62;
          bool canSearch = 63;
          bool hasDetailProperties = 64;
          FileDetailProperties detailProperties = 65;
          bool canOfflineDownload = 66;
          bool canAddShareLink = 67;
          uint64 dirCacheTimeToLiveSecs = 68;
          bool canDeletePermanently = 69;
          map<uint32, string> fileHashes = 70;
          FileEncryptionType fileEncryptionType = 71;
          bool CanCreateEncryptedFolder = 72;
          bool CanLock = 73;
          bool CanSyncFileChangesFromCloud = 74;
          bool supportOfflineDownloadManagement = 75;
          DownloadUrlPathInfo downloadUrlPath = 76;
        }
        message CreateFolderRequest {
          string parentPath = 1;
          string folderName = 2;
        }
        message CreateFolderResult {
          CloudDriveFile folderCreated = 1;
          FileOperationResult result = 2;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        """
        arg = to_message(clouddrive.pb2.CreateFolderRequest, arg)
        if async_:
            return self.async_stub.CreateFolder(arg, metadata=self.metadata)
        else:
            return self.stub.CreateFolder(arg, metadata=self.metadata)

    @overload
    def CreateToken(
        self, 
        arg: dict | clouddrive.pb2.CreateTokenRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.TokenInfo:
        ...
    @overload
    def CreateToken(
        self, 
        arg: dict | clouddrive.pb2.CreateTokenRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        ...
    def CreateToken(
        self, 
        arg: dict | clouddrive.pb2.CreateTokenRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.TokenInfo | Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc CreateToken(CreateTokenRequest) returns (TokenInfo);

        ------------------- protobuf type definition -------------------

        message CreateTokenRequest {
          string rootDir = 1;
          TokenPermissions permissions = 2;
          string friendly_name = 3;
          uint64 expires_in = 4;
        }
        message TokenInfo {
          string token = 1;
          string rootDir = 2;
          TokenPermissions permissions = 3;
          uint64 expires_in = 4;
          string friendly_name = 5;
        }
        message TokenPermissions {
          bool allow_list = 1;
          bool allow_search = 2;
          bool allow_list_local = 3;
          bool allow_create_folder = 4;
          bool allow_create_file = 5;
          bool allow_write = 6;
          bool allow_read = 7;
          bool allow_rename = 8;
          bool allow_move = 9;
          bool allow_copy = 10;
          bool allow_delete = 11;
          bool allow_delete_permanently = 12;
          bool allow_create_encrypt = 13;
          bool allow_unlock_encrypted = 14;
          bool allow_lock_encrypted = 15;
          bool allow_add_offline_download = 16;
          bool allow_list_offline_downloads = 17;
          bool allow_modify_offline_downloads = 18;
          bool allow_shared_links = 19;
          bool allow_view_properties = 20;
          bool allow_get_space_info = 21;
          bool allow_view_runtime_info = 22;
          bool allow_get_memberships = 23;
          bool allow_modify_memberships = 24;
          bool allow_get_mounts = 25;
          bool allow_modify_mounts = 26;
          bool allow_get_transfer_tasks = 27;
          bool allow_modify_transfer_tasks = 28;
          bool allow_get_cloud_apis = 29;
          bool allow_modify_cloud_apis = 30;
          bool allow_get_system_settings = 31;
          bool allow_modify_system_settings = 32;
          bool allow_get_backups = 33;
          bool allow_modify_backups = 34;
          bool allow_get_dav_config = 35;
          bool allow_modify_dav_config = 36;
          bool allow_token_management = 37;
          bool allow_get_account_info = 38;
          bool allow_modify_account = 39;
          bool allow_service_control = 40;
        }
        """
        arg = to_message(clouddrive.pb2.CreateTokenRequest, arg)
        if async_:
            return self.async_stub.CreateToken(arg, metadata=self.metadata)
        else:
            return self.stub.CreateToken(arg, metadata=self.metadata)

    @overload
    def DeleteFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def DeleteFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def DeleteFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc DeleteFile(FileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.DeleteFile(arg, metadata=self.metadata)
        else:
            return self.stub.DeleteFile(arg, metadata=self.metadata)

    @overload
    def DeleteFilePermanently(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def DeleteFilePermanently(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def DeleteFilePermanently(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc DeleteFilePermanently(FileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.DeleteFilePermanently(arg, metadata=self.metadata)
        else:
            return self.stub.DeleteFilePermanently(arg, metadata=self.metadata)

    @overload
    def DeleteFiles(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def DeleteFiles(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def DeleteFiles(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc DeleteFiles(MultiFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message MultiFileRequest {
          repeated string path = 1;
        }
        """
        arg = to_message(clouddrive.pb2.MultiFileRequest, arg)
        if async_:
            return self.async_stub.DeleteFiles(arg, metadata=self.metadata)
        else:
            return self.stub.DeleteFiles(arg, metadata=self.metadata)

    @overload
    def DeleteFilesPermanently(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def DeleteFilesPermanently(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def DeleteFilesPermanently(
        self, 
        arg: dict | clouddrive.pb2.MultiFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc DeleteFilesPermanently(MultiFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message MultiFileRequest {
          repeated string path = 1;
        }
        """
        arg = to_message(clouddrive.pb2.MultiFileRequest, arg)
        if async_:
            return self.async_stub.DeleteFilesPermanently(arg, metadata=self.metadata)
        else:
            return self.stub.DeleteFilesPermanently(arg, metadata=self.metadata)

    @overload
    def DownloadUpdate(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def DownloadUpdate(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def DownloadUpdate(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc DownloadUpdate(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.DownloadUpdate(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.DownloadUpdate(Empty(), metadata=self.metadata)
            return None

    @overload
    def FindFileByPath(
        self, 
        arg: dict | clouddrive.pb2.FindFileByPathRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CloudDriveFile:
        ...
    @overload
    def FindFileByPath(
        self, 
        arg: dict | clouddrive.pb2.FindFileByPathRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CloudDriveFile]:
        ...
    def FindFileByPath(
        self, 
        arg: dict | clouddrive.pb2.FindFileByPathRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CloudDriveFile | Coroutine[Any, Any, clouddrive.pb2.CloudDriveFile]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc FindFileByPath(FindFileByPathRequest) returns (CloudDriveFile);

        ------------------- protobuf type definition -------------------

        message CloudAPI {
          string name = 1;
          string userName = 2;
          string nickName = 3;
          bool isLocked = 4;
          bool supportMultiThreadUploading = 5;
          bool supportQpsLimit = 6;
          bool isCloudEventListenerRunning = 7;
          bool hasPromotions = 8;
          string promotionTitle = 9;
          string path = 10;
        }
        message CloudDriveFile {
          string id = 1;
          string name = 2;
          string fullPathName = 3;
          int64 size = 4;
          FileType fileType = 5;
          google.protobuf.Timestamp createTime = 6;
          google.protobuf.Timestamp writeTime = 7;
          google.protobuf.Timestamp accessTime = 8;
          CloudAPI CloudAPI = 9;
          string thumbnailUrl = 10;
          string previewUrl = 11;
          string originalPath = 14;
          bool isDirectory = 30;
          bool isRoot = 31;
          bool isCloudRoot = 32;
          bool isCloudDirectory = 33;
          bool isCloudFile = 34;
          bool isSearchResult = 35;
          bool isForbidden = 36;
          bool isLocal = 37;
          bool canMount = 60;
          bool canUnmount = 61;
          bool canDirectAccessThumbnailURL = 62;
          bool canSearch = 63;
          bool hasDetailProperties = 64;
          FileDetailProperties detailProperties = 65;
          bool canOfflineDownload = 66;
          bool canAddShareLink = 67;
          uint64 dirCacheTimeToLiveSecs = 68;
          bool canDeletePermanently = 69;
          map<uint32, string> fileHashes = 70;
          FileEncryptionType fileEncryptionType = 71;
          bool CanCreateEncryptedFolder = 72;
          bool CanLock = 73;
          bool CanSyncFileChangesFromCloud = 74;
          bool supportOfflineDownloadManagement = 75;
          DownloadUrlPathInfo downloadUrlPath = 76;
        }
        message DownloadUrlPathInfo {
          string downloadUrlPath = 1;
          int64 expiresIn = 2;
        }
        message FileDetailProperties {
          int64 totalFileCount = 1;
          int64 totalFolderCount = 2;
          int64 totalSize = 3;
          bool isFaved = 4;
          bool isShared = 5;
          string originalPath = 6;
        }
        enum FileEncryptionType {
          FileEncryptionType_None = 0;
          FileEncryptionType_Encrypted = 1;
          FileEncryptionType_Unlocked = 2;
        }
        enum FileType {
          FileType_Directory = 0;
          FileType_File = 1;
          FileType_Other = 2;
        }
        message FindFileByPathRequest {
          string parentPath = 1;
          string path = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FindFileByPathRequest, arg)
        if async_:
            return self.async_stub.FindFileByPath(arg, metadata=self.metadata)
        else:
            return self.stub.FindFileByPath(arg, metadata=self.metadata)

    @overload
    def ForceExpireDirCache(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ForceExpireDirCache(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ForceExpireDirCache(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ForceExpireDirCache(FileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ForceExpireDirCache(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ForceExpireDirCache(arg, metadata=self.metadata)
            return None

    @overload
    def GetAccountStatus(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.AccountStatusResult:
        ...
    @overload
    def GetAccountStatus(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.AccountStatusResult]:
        ...
    def GetAccountStatus(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.AccountStatusResult | Coroutine[Any, Any, clouddrive.pb2.AccountStatusResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetAccountStatus(google.protobuf.Empty) returns (AccountStatusResult);

        ------------------- protobuf type definition -------------------

        message AccountPlan {
          string planName = 1;
          string description = 2;
          string fontAwesomeIcon = 3;
          string durationDescription = 4;
          google.protobuf.Timestamp endTime = 5;
        }
        message AccountRole {
          string roleName = 1;
          string description = 2;
          int32 value = 3;
        }
        message AccountStatusResult {
          string userName = 1;
          string emailConfirmed = 2;
          double accountBalance = 3;
          AccountPlan accountPlan = 4;
          repeated AccountRole accountRoles = 5;
          AccountPlan secondPlan = 6;
          string partnerReferralCode = 7;
          bool trustedDevice = 8;
          bool userNameIsDeviceId = 9;
        }
        """
        if async_:
            return self.async_stub.GetAccountStatus(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetAccountStatus(Empty(), metadata=self.metadata)

    @overload
    def GetAllCloudApis(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CloudAPIList:
        ...
    @overload
    def GetAllCloudApis(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CloudAPIList]:
        ...
    def GetAllCloudApis(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CloudAPIList | Coroutine[Any, Any, clouddrive.pb2.CloudAPIList]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetAllCloudApis(google.protobuf.Empty) returns (CloudAPIList);

        ------------------- protobuf type definition -------------------

        message CloudAPI {
          string name = 1;
          string userName = 2;
          string nickName = 3;
          bool isLocked = 4;
          bool supportMultiThreadUploading = 5;
          bool supportQpsLimit = 6;
          bool isCloudEventListenerRunning = 7;
          bool hasPromotions = 8;
          string promotionTitle = 9;
          string path = 10;
        }
        message CloudAPIList {
          repeated CloudAPI apis = 1;
        }
        """
        if async_:
            return self.async_stub.GetAllCloudApis(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetAllCloudApis(Empty(), metadata=self.metadata)

    @overload
    def GetAllTasksCount(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetAllTasksCountResult:
        ...
    @overload
    def GetAllTasksCount(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetAllTasksCountResult]:
        ...
    def GetAllTasksCount(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetAllTasksCountResult | Coroutine[Any, Any, clouddrive.pb2.GetAllTasksCountResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetAllTasksCount(google.protobuf.Empty) returns (GetAllTasksCountResult);

        ------------------- protobuf type definition -------------------

        message GetAllTasksCountResult {
          uint32 downloadCount = 1;
          uint32 uploadCount = 2;
          uint32 copyTaskCount = 6;
          PushMessage pushMessage = 3;
          bool hasUpdate = 4;
          repeated UploadFileInfo uploadFileStatusChanges = 5;
        }
        message PushMessage {
          string clouddriveVersion = 1;
        }
        message UploadFileInfo {
          string key = 1;
          string destPath = 2;
          uint64 size = 3;
          uint64 transferedBytes = 4;
          string status = 5;
          string errorMessage = 6;
          OperatorType operatorType = 7;
          Status statusEnum = 8;
        }
        """
        if async_:
            return self.async_stub.GetAllTasksCount(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetAllTasksCount(Empty(), metadata=self.metadata)

    @overload
    def GetApiTokenInfo(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.TokenInfo:
        ...
    @overload
    def GetApiTokenInfo(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        ...
    def GetApiTokenInfo(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.TokenInfo | Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetApiTokenInfo(StringValue) returns (TokenInfo);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        message TokenInfo {
          string token = 1;
          string rootDir = 2;
          TokenPermissions permissions = 3;
          uint64 expires_in = 4;
          string friendly_name = 5;
        }
        message TokenPermissions {
          bool allow_list = 1;
          bool allow_search = 2;
          bool allow_list_local = 3;
          bool allow_create_folder = 4;
          bool allow_create_file = 5;
          bool allow_write = 6;
          bool allow_read = 7;
          bool allow_rename = 8;
          bool allow_move = 9;
          bool allow_copy = 10;
          bool allow_delete = 11;
          bool allow_delete_permanently = 12;
          bool allow_create_encrypt = 13;
          bool allow_unlock_encrypted = 14;
          bool allow_lock_encrypted = 15;
          bool allow_add_offline_download = 16;
          bool allow_list_offline_downloads = 17;
          bool allow_modify_offline_downloads = 18;
          bool allow_shared_links = 19;
          bool allow_view_properties = 20;
          bool allow_get_space_info = 21;
          bool allow_view_runtime_info = 22;
          bool allow_get_memberships = 23;
          bool allow_modify_memberships = 24;
          bool allow_get_mounts = 25;
          bool allow_modify_mounts = 26;
          bool allow_get_transfer_tasks = 27;
          bool allow_modify_transfer_tasks = 28;
          bool allow_get_cloud_apis = 29;
          bool allow_modify_cloud_apis = 30;
          bool allow_get_system_settings = 31;
          bool allow_modify_system_settings = 32;
          bool allow_get_backups = 33;
          bool allow_modify_backups = 34;
          bool allow_get_dav_config = 35;
          bool allow_modify_dav_config = 36;
          bool allow_token_management = 37;
          bool allow_get_account_info = 38;
          bool allow_modify_account = 39;
          bool allow_service_control = 40;
        }
        """
        arg = to_message(clouddrive.pb2.StringValue, arg)
        if async_:
            return self.async_stub.GetApiTokenInfo(arg, metadata=self.metadata)
        else:
            return self.stub.GetApiTokenInfo(arg, metadata=self.metadata)

    @overload
    def GetAvailableDriveLetters(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetAvailableDriveLettersResult:
        ...
    @overload
    def GetAvailableDriveLetters(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetAvailableDriveLettersResult]:
        ...
    def GetAvailableDriveLetters(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetAvailableDriveLettersResult | Coroutine[Any, Any, clouddrive.pb2.GetAvailableDriveLettersResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetAvailableDriveLetters(google.protobuf.Empty) returns (GetAvailableDriveLettersResult);

        ------------------- protobuf type definition -------------------

        message GetAvailableDriveLettersResult {
          repeated string driveLetters = 1;
        }
        """
        if async_:
            return self.async_stub.GetAvailableDriveLetters(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetAvailableDriveLetters(Empty(), metadata=self.metadata)

    @overload
    def GetBalanceLog(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BalanceLogResult:
        ...
    @overload
    def GetBalanceLog(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BalanceLogResult]:
        ...
    def GetBalanceLog(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BalanceLogResult | Coroutine[Any, Any, clouddrive.pb2.BalanceLogResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetBalanceLog(google.protobuf.Empty) returns (BalanceLogResult);

        ------------------- protobuf type definition -------------------

        message BalanceLog {
          double balance_before = 1;
          double balance_after = 2;
          double balance_change = 3;
          BalancceChangeOperation operation = 4;
          string operation_source = 5;
          string operation_id = 6;
          google.protobuf.Timestamp operation_time = 7;
        }
        message BalanceLogResult {
          repeated BalanceLog logs = 1;
        }
        """
        if async_:
            return self.async_stub.GetBalanceLog(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetBalanceLog(Empty(), metadata=self.metadata)

    @overload
    def GetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.GetCloudAPIConfigRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CloudAPIConfig:
        ...
    @overload
    def GetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.GetCloudAPIConfigRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CloudAPIConfig]:
        ...
    def GetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.GetCloudAPIConfigRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CloudAPIConfig | Coroutine[Any, Any, clouddrive.pb2.CloudAPIConfig]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetCloudAPIConfig(GetCloudAPIConfigRequest) returns (CloudAPIConfig);

        ------------------- protobuf type definition -------------------

        message CloudAPIConfig {
          uint32 maxDownloadThreads = 1;
          uint64 minReadLengthKB = 2;
          uint64 maxReadLengthKB = 3;
          uint64 defaultReadLengthKB = 4;
          uint64 maxBufferPoolSizeMB = 5;
          double maxQueriesPerSecond = 6;
          bool forceIpv4 = 7;
          ProxyInfo apiProxy = 8;
          ProxyInfo dataProxy = 9;
          string customUserAgent = 10;
          uint32 maxUploadThreads = 11;
          bool insecureTls = 12;
        }
        message GetCloudAPIConfigRequest {
          string cloudName = 1;
          string userName = 2;
        }
        message ProxyInfo {
          ProxyType proxyType = 1;
          string host = 2;
          uint32 port = 3;
          string username = 4;
          string password = 5;
        }
        """
        arg = to_message(clouddrive.pb2.GetCloudAPIConfigRequest, arg)
        if async_:
            return self.async_stub.GetCloudAPIConfig(arg, metadata=self.metadata)
        else:
            return self.stub.GetCloudAPIConfig(arg, metadata=self.metadata)

    @overload
    def GetCloudDrive1UserData(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringResult:
        ...
    @overload
    def GetCloudDrive1UserData(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        ...
    def GetCloudDrive1UserData(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringResult | Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetCloudDrive1UserData(google.protobuf.Empty) returns (StringResult);

        ------------------- protobuf type definition -------------------

        message StringResult {
          string result = 1;
        }
        """
        if async_:
            return self.async_stub.GetCloudDrive1UserData(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetCloudDrive1UserData(Empty(), metadata=self.metadata)

    @overload
    def GetCloudDrivePlans(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetCloudDrivePlansResult:
        ...
    @overload
    def GetCloudDrivePlans(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetCloudDrivePlansResult]:
        ...
    def GetCloudDrivePlans(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetCloudDrivePlansResult | Coroutine[Any, Any, clouddrive.pb2.GetCloudDrivePlansResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetCloudDrivePlans(google.protobuf.Empty) returns (GetCloudDrivePlansResult);

        ------------------- protobuf type definition -------------------

        message CloudDrivePlan {
          string id = 1;
          string name = 2;
          string description = 3;
          double price = 4;
          int64 duration = 5;
          string durationDescription = 6;
          bool isActive = 7;
          string fontAwesomeIcon = 8;
          double originalPrice = 9;
          repeated AccountRole planRoles = 10;
        }
        message GetCloudDrivePlansResult {
          repeated CloudDrivePlan plans = 1;
        }
        """
        if async_:
            return self.async_stub.GetCloudDrivePlans(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetCloudDrivePlans(Empty(), metadata=self.metadata)

    @overload
    def GetCloudMemberships(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CloudMemberships:
        ...
    @overload
    def GetCloudMemberships(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CloudMemberships]:
        ...
    def GetCloudMemberships(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CloudMemberships | Coroutine[Any, Any, clouddrive.pb2.CloudMemberships]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetCloudMemberships(FileRequest) returns (CloudMemberships);

        ------------------- protobuf type definition -------------------

        message CloudMembership {
          string identity = 1;
          google.protobuf.Timestamp expireTime = 2;
          string level = 3;
        }
        message CloudMemberships {
          repeated CloudMembership memberships = 1;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetCloudMemberships(arg, metadata=self.metadata)
        else:
            return self.stub.GetCloudMemberships(arg, metadata=self.metadata)

    @overload
    def GetCopyTasks(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetCopyTaskResult:
        ...
    @overload
    def GetCopyTasks(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetCopyTaskResult]:
        ...
    def GetCopyTasks(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetCopyTaskResult | Coroutine[Any, Any, clouddrive.pb2.GetCopyTaskResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetCopyTasks(google.protobuf.Empty) returns (GetCopyTaskResult);

        ------------------- protobuf type definition -------------------

        message CopyTask {
          TaskMode taskMode = 2;
          string sourcePath = 3;
          string destPath = 4;
          TaskStatus status = 5;
          uint64 totalFolders = 6;
          uint64 totalFiles = 7;
          uint64 failedFolders = 8;
          uint64 failedFiles = 9;
          uint64 uploadedFiles = 10;
          uint64 cancelledFiles = 11;
          uint64 skippedFiles = 16;
          uint64 totalBytes = 12;
          uint64 uploadedBytes = 13;
          bool paused = 14;
          repeated TaskError errors = 15;
          google.protobuf.Timestamp startTime = 17;
          google.protobuf.Timestamp endTime = 18;
        }
        message GetCopyTaskResult {
          repeated CopyTask copyTasks = 1;
        }
        """
        if async_:
            return self.async_stub.GetCopyTasks(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetCopyTasks(Empty(), metadata=self.metadata)

    @overload
    def GetDavServerConfig(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.DavServerConfig:
        ...
    @overload
    def GetDavServerConfig(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.DavServerConfig]:
        ...
    def GetDavServerConfig(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.DavServerConfig | Coroutine[Any, Any, clouddrive.pb2.DavServerConfig]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDavServerConfig(google.protobuf.Empty) returns (DavServerConfig);

        ------------------- protobuf type definition -------------------

        message DavServerConfig {
          bool davServerEnabled = 1;
          string davServerPath = 2;
          bool enableClouddriveAccount = 3;
          string clouddriveAccountRootPath = 4;
          bool clouddriveAccountReadOnly = 5;
          bool enableAnonymousAccess = 6;
          string anonymousRootPath = 7;
          bool anonymousReadOnly = 8;
          repeated DavUser users = 9;
        }
        message DavUser {
          string userName = 1;
          string password = 2;
          string rootPath = 3;
          bool readOnly = 4;
          bool enabled = 5;
          bool guest = 6;
        }
        """
        if async_:
            return self.async_stub.GetDavServerConfig(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetDavServerConfig(Empty(), metadata=self.metadata)

    @overload
    def GetDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.DavUser:
        ...
    @overload
    def GetDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.DavUser]:
        ...
    def GetDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.DavUser | Coroutine[Any, Any, clouddrive.pb2.DavUser]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDavUser(StringValue) returns (DavUser);

        ------------------- protobuf type definition -------------------

        message DavUser {
          string userName = 1;
          string password = 2;
          string rootPath = 3;
          bool readOnly = 4;
          bool enabled = 5;
          bool guest = 6;
        }
        message StringValue {
          string value = 1;
        }
        """
        arg = to_message(clouddrive.pb2.StringValue, arg)
        if async_:
            return self.async_stub.GetDavUser(arg, metadata=self.metadata)
        else:
            return self.stub.GetDavUser(arg, metadata=self.metadata)

    @overload
    def GetDirCacheTable(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.DirCacheTable:
        ...
    @overload
    def GetDirCacheTable(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.DirCacheTable]:
        ...
    def GetDirCacheTable(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.DirCacheTable | Coroutine[Any, Any, clouddrive.pb2.DirCacheTable]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDirCacheTable(google.protobuf.Empty) returns (DirCacheTable);

        ------------------- protobuf type definition -------------------

        message DirCacheTable {
          map<string, DirCacheItem> dirCacheTable = 1;
        }
        """
        if async_:
            return self.async_stub.GetDirCacheTable(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetDirCacheTable(Empty(), metadata=self.metadata)

    @overload
    def GetDownloadFileCount(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetDownloadFileCountResult:
        ...
    @overload
    def GetDownloadFileCount(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetDownloadFileCountResult]:
        ...
    def GetDownloadFileCount(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetDownloadFileCountResult | Coroutine[Any, Any, clouddrive.pb2.GetDownloadFileCountResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDownloadFileCount(google.protobuf.Empty) returns (GetDownloadFileCountResult);

        ------------------- protobuf type definition -------------------

        message GetDownloadFileCountResult {
          uint32 fileCount = 1;
        }
        """
        if async_:
            return self.async_stub.GetDownloadFileCount(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetDownloadFileCount(Empty(), metadata=self.metadata)

    @overload
    def GetDownloadFileList(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetDownloadFileListResult:
        ...
    @overload
    def GetDownloadFileList(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetDownloadFileListResult]:
        ...
    def GetDownloadFileList(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetDownloadFileListResult | Coroutine[Any, Any, clouddrive.pb2.GetDownloadFileListResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDownloadFileList(google.protobuf.Empty) returns (GetDownloadFileListResult);

        ------------------- protobuf type definition -------------------

        message DownloadFileInfo {
          string filePath = 1;
          uint64 fileLength = 2;
          uint64 totalBufferUsed = 3;
          uint32 downloadThreadCount = 4;
          repeated string process = 5;
          string detailDownloadInfo = 6;
          string lastDownloadError = 7;
          double bytesPerSecond = 8;
        }
        message GetDownloadFileListResult {
          double globalBytesPerSecond = 1;
          repeated DownloadFileInfo downloadFiles = 4;
        }
        """
        if async_:
            return self.async_stub.GetDownloadFileList(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetDownloadFileList(Empty(), metadata=self.metadata)

    @overload
    def GetDownloadUrlPath(
        self, 
        arg: dict | clouddrive.pb2.GetDownloadUrlPathRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.DownloadUrlPathInfo:
        ...
    @overload
    def GetDownloadUrlPath(
        self, 
        arg: dict | clouddrive.pb2.GetDownloadUrlPathRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.DownloadUrlPathInfo]:
        ...
    def GetDownloadUrlPath(
        self, 
        arg: dict | clouddrive.pb2.GetDownloadUrlPathRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.DownloadUrlPathInfo | Coroutine[Any, Any, clouddrive.pb2.DownloadUrlPathInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetDownloadUrlPath(GetDownloadUrlPathRequest) returns (DownloadUrlPathInfo);

        ------------------- protobuf type definition -------------------

        message DownloadUrlPathInfo {
          string downloadUrlPath = 1;
          int64 expiresIn = 2;
        }
        message GetDownloadUrlPathRequest {
          string path = 1;
          bool preview = 2;
        }
        """
        arg = to_message(clouddrive.pb2.GetDownloadUrlPathRequest, arg)
        if async_:
            return self.async_stub.GetDownloadUrlPath(arg, metadata=self.metadata)
        else:
            return self.stub.GetDownloadUrlPath(arg, metadata=self.metadata)

    @overload
    def GetEffectiveDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.GetEffectiveDirCacheTimeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetEffectiveDirCacheTimeResult:
        ...
    @overload
    def GetEffectiveDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.GetEffectiveDirCacheTimeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetEffectiveDirCacheTimeResult]:
        ...
    def GetEffectiveDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.GetEffectiveDirCacheTimeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetEffectiveDirCacheTimeResult | Coroutine[Any, Any, clouddrive.pb2.GetEffectiveDirCacheTimeResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetEffectiveDirCacheTimeSecs(GetEffectiveDirCacheTimeRequest) returns (GetEffectiveDirCacheTimeResult);

        ------------------- protobuf type definition -------------------

        message GetEffectiveDirCacheTimeRequest {
          string path = 1;
        }
        message GetEffectiveDirCacheTimeResult {
          uint64 dirCacheTimeSecs = 1;
        }
        """
        arg = to_message(clouddrive.pb2.GetEffectiveDirCacheTimeRequest, arg)
        if async_:
            return self.async_stub.GetEffectiveDirCacheTimeSecs(arg, metadata=self.metadata)
        else:
            return self.stub.GetEffectiveDirCacheTimeSecs(arg, metadata=self.metadata)

    @overload
    def GetFileDetailProperties(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileDetailProperties:
        ...
    @overload
    def GetFileDetailProperties(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileDetailProperties]:
        ...
    def GetFileDetailProperties(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileDetailProperties | Coroutine[Any, Any, clouddrive.pb2.FileDetailProperties]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetFileDetailProperties(FileRequest) returns (FileDetailProperties);

        ------------------- protobuf type definition -------------------

        message FileDetailProperties {
          int64 totalFileCount = 1;
          int64 totalFolderCount = 2;
          int64 totalSize = 3;
          bool isFaved = 4;
          bool isShared = 5;
          string originalPath = 6;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetFileDetailProperties(arg, metadata=self.metadata)
        else:
            return self.stub.GetFileDetailProperties(arg, metadata=self.metadata)

    @overload
    def GetMachineId(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringResult:
        ...
    @overload
    def GetMachineId(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        ...
    def GetMachineId(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringResult | Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetMachineId(google.protobuf.Empty) returns (StringResult);

        ------------------- protobuf type definition -------------------

        message StringResult {
          string result = 1;
        }
        """
        if async_:
            return self.async_stub.GetMachineId(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetMachineId(Empty(), metadata=self.metadata)

    @overload
    def GetMergeTasks(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetMergeTasksResult:
        ...
    @overload
    def GetMergeTasks(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetMergeTasksResult]:
        ...
    def GetMergeTasks(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetMergeTasksResult | Coroutine[Any, Any, clouddrive.pb2.GetMergeTasksResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetMergeTasks(google.protobuf.Empty) returns (GetMergeTasksResult);

        ------------------- protobuf type definition -------------------

        message GetMergeTasksResult {
          repeated MergeTask mergeTasks = 1;
        }
        message MergeTask {
          string sourcePath = 1;
          string destPath = 2;
          TaskStatus status = 3;
          uint64 mergedFiles = 4;
          uint64 mergedFolders = 5;
          google.protobuf.Timestamp startTime = 6;
          google.protobuf.Timestamp endTime = 7;
          string errorMessage = 8;
          ConflictPolicy conflictPolicy = 9;
          OperationType operationType = 10;
        }
        """
        if async_:
            return self.async_stub.GetMergeTasks(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetMergeTasks(Empty(), metadata=self.metadata)

    @overload
    def GetMetaData(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileMetaData:
        ...
    @overload
    def GetMetaData(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileMetaData]:
        ...
    def GetMetaData(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileMetaData | Coroutine[Any, Any, clouddrive.pb2.FileMetaData]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetMetaData(FileRequest) returns (FileMetaData);

        ------------------- protobuf type definition -------------------

        message FileMetaData {
          map<string, string> metadata = 1;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetMetaData(arg, metadata=self.metadata)
        else:
            return self.stub.GetMetaData(arg, metadata=self.metadata)

    @overload
    def GetMountPoints(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetMountPointsResult:
        ...
    @overload
    def GetMountPoints(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetMountPointsResult]:
        ...
    def GetMountPoints(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetMountPointsResult | Coroutine[Any, Any, clouddrive.pb2.GetMountPointsResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetMountPoints(google.protobuf.Empty) returns (GetMountPointsResult);

        ------------------- protobuf type definition -------------------

        message GetMountPointsResult {
          repeated MountPoint mountPoints = 1;
        }
        message MountPoint {
          string mountPoint = 1;
          string sourceDir = 2;
          bool localMount = 3;
          bool readOnly = 4;
          bool autoMount = 5;
          uint32 uid = 6;
          uint32 gid = 7;
          string permissions = 8;
          bool isMounted = 9;
          string failReason = 10;
        }
        """
        if async_:
            return self.async_stub.GetMountPoints(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetMountPoints(Empty(), metadata=self.metadata)

    @overload
    def GetOfflineQuotaInfo(
        self, 
        arg: dict | clouddrive.pb2.OfflineQuotaRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OfflineQuotaInfo:
        ...
    @overload
    def GetOfflineQuotaInfo(
        self, 
        arg: dict | clouddrive.pb2.OfflineQuotaRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OfflineQuotaInfo]:
        ...
    def GetOfflineQuotaInfo(
        self, 
        arg: dict | clouddrive.pb2.OfflineQuotaRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OfflineQuotaInfo | Coroutine[Any, Any, clouddrive.pb2.OfflineQuotaInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetOfflineQuotaInfo(OfflineQuotaRequest) returns (OfflineQuotaInfo);

        ------------------- protobuf type definition -------------------

        message OfflineQuotaInfo {
          int32 total = 1;
          int32 used = 2;
          int32 left = 3;
        }
        message OfflineQuotaRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          string path = 3;
        }
        """
        arg = to_message(clouddrive.pb2.OfflineQuotaRequest, arg)
        if async_:
            return self.async_stub.GetOfflineQuotaInfo(arg, metadata=self.metadata)
        else:
            return self.stub.GetOfflineQuotaInfo(arg, metadata=self.metadata)

    @overload
    def GetOnlineDevices(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OnlineDevices:
        ...
    @overload
    def GetOnlineDevices(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OnlineDevices]:
        ...
    def GetOnlineDevices(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OnlineDevices | Coroutine[Any, Any, clouddrive.pb2.OnlineDevices]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetOnlineDevices(google.protobuf.Empty) returns (OnlineDevices);

        ------------------- protobuf type definition -------------------

        message Device {
          string deviceId = 1;
          string deviceName = 2;
          string osType = 3;
          string version = 4;
          string ipAddress = 5;
          google.protobuf.Timestamp lastUpdateTime = 6;
        }
        message OnlineDevices {
          repeated Device devices = 1;
        }
        """
        if async_:
            return self.async_stub.GetOnlineDevices(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetOnlineDevices(Empty(), metadata=self.metadata)

    @overload
    def GetOpenFileHandles(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OpenFileHandleList:
        ...
    @overload
    def GetOpenFileHandles(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OpenFileHandleList]:
        ...
    def GetOpenFileHandles(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OpenFileHandleList | Coroutine[Any, Any, clouddrive.pb2.OpenFileHandleList]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetOpenFileHandles(google.protobuf.Empty) returns (OpenFileHandleList);

        ------------------- protobuf type definition -------------------

        message OpenFileHandle {
          uint64 fileHandle = 1;
          uint64 processId = 2;
          string processPath = 3;
          string filePath = 4;
          bool isDirectory = 5;
          google.protobuf.Timestamp openTime = 6;
          string specialCommand = 7;
        }
        message OpenFileHandleList {
          repeated OpenFileHandle openFileHandles = 1;
        }
        """
        if async_:
            return self.async_stub.GetOpenFileHandles(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetOpenFileHandles(Empty(), metadata=self.metadata)

    @overload
    def GetOpenFileTable(
        self, 
        arg: dict | clouddrive.pb2.GetOpenFileTableRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OpenFileTable:
        ...
    @overload
    def GetOpenFileTable(
        self, 
        arg: dict | clouddrive.pb2.GetOpenFileTableRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OpenFileTable]:
        ...
    def GetOpenFileTable(
        self, 
        arg: dict | clouddrive.pb2.GetOpenFileTableRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OpenFileTable | Coroutine[Any, Any, clouddrive.pb2.OpenFileTable]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetOpenFileTable(GetOpenFileTableRequest) returns (OpenFileTable);

        ------------------- protobuf type definition -------------------

        message GetOpenFileTableRequest {
          bool includeDir = 1;
        }
        message OpenFileTable {
          map<uint64, string> openFileTable = 1;
          uint64 localOpenFileCount = 2;
        }
        """
        arg = to_message(clouddrive.pb2.GetOpenFileTableRequest, arg)
        if async_:
            return self.async_stub.GetOpenFileTable(arg, metadata=self.metadata)
        else:
            return self.stub.GetOpenFileTable(arg, metadata=self.metadata)

    @overload
    def GetOriginalPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringResult:
        ...
    @overload
    def GetOriginalPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        ...
    def GetOriginalPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringResult | Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetOriginalPath(FileRequest) returns (StringResult);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message StringResult {
          string result = 1;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetOriginalPath(arg, metadata=self.metadata)
        else:
            return self.stub.GetOriginalPath(arg, metadata=self.metadata)

    @overload
    def GetPromotions(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetPromotionsResult:
        ...
    @overload
    def GetPromotions(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetPromotionsResult]:
        ...
    def GetPromotions(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetPromotionsResult | Coroutine[Any, Any, clouddrive.pb2.GetPromotionsResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetPromotions(google.protobuf.Empty) returns (GetPromotionsResult);

        ------------------- protobuf type definition -------------------

        message GetPromotionsResult {
          repeated Promotion promotions = 1;
        }
        message Promotion {
          string id = 1;
          string cloudName = 2;
          string title = 3;
          string subTitle = 4;
          string rules = 5;
          string notice = 6;
          string url = 7;
        }
        """
        if async_:
            return self.async_stub.GetPromotions(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetPromotions(Empty(), metadata=self.metadata)

    @overload
    def GetPromotionsByCloud(
        self, 
        arg: dict | clouddrive.pb2.CloudAPIRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetPromotionsResult:
        ...
    @overload
    def GetPromotionsByCloud(
        self, 
        arg: dict | clouddrive.pb2.CloudAPIRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetPromotionsResult]:
        ...
    def GetPromotionsByCloud(
        self, 
        arg: dict | clouddrive.pb2.CloudAPIRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetPromotionsResult | Coroutine[Any, Any, clouddrive.pb2.GetPromotionsResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetPromotionsByCloud(CloudAPIRequest) returns (GetPromotionsResult);

        ------------------- protobuf type definition -------------------

        message CloudAPIRequest {
          string cloudName = 1;
          string userName = 2;
        }
        message GetPromotionsResult {
          repeated Promotion promotions = 1;
        }
        message Promotion {
          string id = 1;
          string cloudName = 2;
          string title = 3;
          string subTitle = 4;
          string rules = 5;
          string notice = 6;
          string url = 7;
        }
        """
        arg = to_message(clouddrive.pb2.CloudAPIRequest, arg)
        if async_:
            return self.async_stub.GetPromotionsByCloud(arg, metadata=self.metadata)
        else:
            return self.stub.GetPromotionsByCloud(arg, metadata=self.metadata)

    @overload
    def GetReferencedEntryPaths(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringList:
        ...
    @overload
    def GetReferencedEntryPaths(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringList]:
        ...
    def GetReferencedEntryPaths(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringList | Coroutine[Any, Any, clouddrive.pb2.StringList]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetReferencedEntryPaths(FileRequest) returns (StringList);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message StringList {
          repeated string values = 1;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetReferencedEntryPaths(arg, metadata=self.metadata)
        else:
            return self.stub.GetReferencedEntryPaths(arg, metadata=self.metadata)

    @overload
    def GetReferralCode(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringValue:
        ...
    @overload
    def GetReferralCode(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringValue]:
        ...
    def GetReferralCode(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringValue | Coroutine[Any, Any, clouddrive.pb2.StringValue]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetReferralCode(google.protobuf.Empty) returns (StringValue);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            return self.async_stub.GetReferralCode(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetReferralCode(Empty(), metadata=self.metadata)

    @overload
    def GetRunningInfo(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.RunInfo:
        ...
    @overload
    def GetRunningInfo(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.RunInfo]:
        ...
    def GetRunningInfo(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.RunInfo | Coroutine[Any, Any, clouddrive.pb2.RunInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetRunningInfo(google.protobuf.Empty) returns (RunInfo);

        ------------------- protobuf type definition -------------------

        message RunInfo {
          double cpuUsage = 1;
          uint64 memUsageKB = 2;
          double uptime = 3;
          uint64 fhTableCount = 4;
          uint64 dirCacheCount = 5;
          uint64 tempFileCount = 6;
          uint64 dbDirCacheCount = 7;
          double downloadBytesPerSecond = 8;
          double uploadBytesPerSecond = 9;
          uint64 totalMemoryKB = 10;
        }
        """
        if async_:
            return self.async_stub.GetRunningInfo(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetRunningInfo(Empty(), metadata=self.metadata)

    @overload
    def GetRuntimeInfo(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.RuntimeInfo:
        ...
    @overload
    def GetRuntimeInfo(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.RuntimeInfo]:
        ...
    def GetRuntimeInfo(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.RuntimeInfo | Coroutine[Any, Any, clouddrive.pb2.RuntimeInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetRuntimeInfo(google.protobuf.Empty) returns (RuntimeInfo);

        ------------------- protobuf type definition -------------------

        message RuntimeInfo {
          string productName = 1;
          string productVersion = 2;
          string CloudAPIVersion = 3;
          string osInfo = 4;
        }
        """
        if async_:
            return self.async_stub.GetRuntimeInfo(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetRuntimeInfo(Empty(), metadata=self.metadata)

    @overload
    def GetSearchResults(
        self, 
        arg: dict | clouddrive.pb2.SearchRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.SubFilesReply]:
        ...
    @overload
    def GetSearchResults(
        self, 
        arg: dict | clouddrive.pb2.SearchRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.SubFilesReply]]:
        ...
    def GetSearchResults(
        self, 
        arg: dict | clouddrive.pb2.SearchRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.SubFilesReply] | Coroutine[Any, Any, Iterable[clouddrive.pb2.SubFilesReply]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetSearchResults(SearchRequest) returns (stream SubFilesReply);

        ------------------- protobuf type definition -------------------

        message CloudDriveFile {
          string id = 1;
          string name = 2;
          string fullPathName = 3;
          int64 size = 4;
          FileType fileType = 5;
          google.protobuf.Timestamp createTime = 6;
          google.protobuf.Timestamp writeTime = 7;
          google.protobuf.Timestamp accessTime = 8;
          CloudAPI CloudAPI = 9;
          string thumbnailUrl = 10;
          string previewUrl = 11;
          string originalPath = 14;
          bool isDirectory = 30;
          bool isRoot = 31;
          bool isCloudRoot = 32;
          bool isCloudDirectory = 33;
          bool isCloudFile = 34;
          bool isSearchResult = 35;
          bool isForbidden = 36;
          bool isLocal = 37;
          bool canMount = 60;
          bool canUnmount = 61;
          bool canDirectAccessThumbnailURL = 62;
          bool canSearch = 63;
          bool hasDetailProperties = 64;
          FileDetailProperties detailProperties = 65;
          bool canOfflineDownload = 66;
          bool canAddShareLink = 67;
          uint64 dirCacheTimeToLiveSecs = 68;
          bool canDeletePermanently = 69;
          map<uint32, string> fileHashes = 70;
          FileEncryptionType fileEncryptionType = 71;
          bool CanCreateEncryptedFolder = 72;
          bool CanLock = 73;
          bool CanSyncFileChangesFromCloud = 74;
          bool supportOfflineDownloadManagement = 75;
          DownloadUrlPathInfo downloadUrlPath = 76;
        }
        message SearchRequest {
          string path = 1;
          string searchFor = 2;
          bool forceRefresh = 3;
          bool fuzzyMatch = 4;
        }
        message SubFilesReply {
          repeated CloudDriveFile subFiles = 1;
        }
        """
        arg = to_message(clouddrive.pb2.SearchRequest, arg)
        if async_:
            return self.async_stub.GetSearchResults(arg, metadata=self.metadata)
        else:
            return self.stub.GetSearchResults(arg, metadata=self.metadata)

    @overload
    def GetSpaceInfo(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.SpaceInfo:
        ...
    @overload
    def GetSpaceInfo(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.SpaceInfo]:
        ...
    def GetSpaceInfo(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.SpaceInfo | Coroutine[Any, Any, clouddrive.pb2.SpaceInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetSpaceInfo(FileRequest) returns (SpaceInfo);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message SpaceInfo {
          int64 totalSpace = 1;
          int64 usedSpace = 2;
          int64 freeSpace = 3;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.GetSpaceInfo(arg, metadata=self.metadata)
        else:
            return self.stub.GetSpaceInfo(arg, metadata=self.metadata)

    @overload
    def GetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.ListSubFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.SubFilesReply]:
        ...
    @overload
    def GetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.ListSubFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.SubFilesReply]]:
        ...
    def GetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.ListSubFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.SubFilesReply] | Coroutine[Any, Any, Iterable[clouddrive.pb2.SubFilesReply]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetSubFiles(ListSubFileRequest) returns (stream SubFilesReply);

        ------------------- protobuf type definition -------------------

        message CloudDriveFile {
          string id = 1;
          string name = 2;
          string fullPathName = 3;
          int64 size = 4;
          FileType fileType = 5;
          google.protobuf.Timestamp createTime = 6;
          google.protobuf.Timestamp writeTime = 7;
          google.protobuf.Timestamp accessTime = 8;
          CloudAPI CloudAPI = 9;
          string thumbnailUrl = 10;
          string previewUrl = 11;
          string originalPath = 14;
          bool isDirectory = 30;
          bool isRoot = 31;
          bool isCloudRoot = 32;
          bool isCloudDirectory = 33;
          bool isCloudFile = 34;
          bool isSearchResult = 35;
          bool isForbidden = 36;
          bool isLocal = 37;
          bool canMount = 60;
          bool canUnmount = 61;
          bool canDirectAccessThumbnailURL = 62;
          bool canSearch = 63;
          bool hasDetailProperties = 64;
          FileDetailProperties detailProperties = 65;
          bool canOfflineDownload = 66;
          bool canAddShareLink = 67;
          uint64 dirCacheTimeToLiveSecs = 68;
          bool canDeletePermanently = 69;
          map<uint32, string> fileHashes = 70;
          FileEncryptionType fileEncryptionType = 71;
          bool CanCreateEncryptedFolder = 72;
          bool CanLock = 73;
          bool CanSyncFileChangesFromCloud = 74;
          bool supportOfflineDownloadManagement = 75;
          DownloadUrlPathInfo downloadUrlPath = 76;
        }
        message ListSubFileRequest {
          string path = 1;
          bool forceRefresh = 2;
          bool checkExpires = 3;
        }
        message SubFilesReply {
          repeated CloudDriveFile subFiles = 1;
        }
        """
        arg = to_message(clouddrive.pb2.ListSubFileRequest, arg)
        if async_:
            return self.async_stub.GetSubFiles(arg, metadata=self.metadata)
        else:
            return self.stub.GetSubFiles(arg, metadata=self.metadata)

    @overload
    def GetSystemInfo(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.CloudDriveSystemInfo:
        ...
    @overload
    def GetSystemInfo(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.CloudDriveSystemInfo]:
        ...
    def GetSystemInfo(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.CloudDriveSystemInfo | Coroutine[Any, Any, clouddrive.pb2.CloudDriveSystemInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetSystemInfo(google.protobuf.Empty) returns (CloudDriveSystemInfo);

        ------------------- protobuf type definition -------------------

        message CloudDriveSystemInfo {
          bool IsLogin = 1;
          string UserName = 2;
          bool SystemReady = 3;
          string SystemMessage = 4;
          bool hasError = 5;
        }
        """
        if async_:
            return self.async_stub.GetSystemInfo(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetSystemInfo(Empty(), metadata=self.metadata)

    @overload
    def GetSystemSettings(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.SystemSettings:
        ...
    @overload
    def GetSystemSettings(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.SystemSettings]:
        ...
    def GetSystemSettings(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.SystemSettings | Coroutine[Any, Any, clouddrive.pb2.SystemSettings]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetSystemSettings(google.protobuf.Empty) returns (SystemSettings);

        ------------------- protobuf type definition -------------------

        enum LogLevel {
          LogLevel_Trace = 0;
          LogLevel_Debug = 1;
          LogLevel_Info = 2;
          LogLevel_Warn = 3;
          LogLevel_Error = 4;
        }
        message ProxyInfo {
          ProxyType proxyType = 1;
          string host = 2;
          uint32 port = 3;
          string username = 4;
          string password = 5;
        }
        message StringList {
          repeated string values = 1;
        }
        message SystemSettings {
          uint64 dirCacheTimeToLiveSecs = 1;
          uint64 maxPreProcessTasks = 2;
          uint64 maxProcessTasks = 3;
          string tempFileLocation = 4;
          bool syncWithCloud = 5;
          uint64 readDownloaderTimeoutSecs = 6;
          uint64 uploadDelaySecs = 7;
          StringList processBlackList = 8;
          StringList uploadIgnoredExtensions = 9;
          UpdateChannel updateChannel = 10;
          double maxDownloadSpeedKBytesPerSecond = 11;
          double maxUploadSpeedKBytesPerSecond = 12;
          string deviceName = 13;
          bool dirCachePersistence = 14;
          string dirCacheDbLocation = 15;
          LogLevel fileLogLevel = 16;
          LogLevel terminalLogLevel = 17;
          LogLevel backupLogLevel = 18;
          bool EnableAutoRegisterDevice = 19;
          LogLevel realtimeLogLevel = 20;
          StringList operatorPriorityOrder = 21;
          ProxyInfo updateProxy = 22;
        }
        enum UpdateChannel {
          UpdateChannel_Release = 0;
          UpdateChannel_Beta = 1;
        }
        """
        if async_:
            return self.async_stub.GetSystemSettings(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetSystemSettings(Empty(), metadata=self.metadata)

    @overload
    def GetTempFileTable(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.TempFileTable:
        ...
    @overload
    def GetTempFileTable(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.TempFileTable]:
        ...
    def GetTempFileTable(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.TempFileTable | Coroutine[Any, Any, clouddrive.pb2.TempFileTable]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetTempFileTable(google.protobuf.Empty) returns (TempFileTable);

        ------------------- protobuf type definition -------------------

        message TempFileTable {
          uint64 count = 1;
          repeated string tempFiles = 2;
        }
        """
        if async_:
            return self.async_stub.GetTempFileTable(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetTempFileTable(Empty(), metadata=self.metadata)

    @overload
    def GetToken(
        self, 
        arg: dict | clouddrive.pb2.GetTokenRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.JWTToken:
        ...
    @overload
    def GetToken(
        self, 
        arg: dict | clouddrive.pb2.GetTokenRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.JWTToken]:
        ...
    def GetToken(
        self, 
        arg: dict | clouddrive.pb2.GetTokenRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.JWTToken | Coroutine[Any, Any, clouddrive.pb2.JWTToken]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetToken(GetTokenRequest) returns (JWTToken);

        ------------------- protobuf type definition -------------------

        message GetTokenRequest {
          string userName = 1;
          string password = 2;
        }
        message JWTToken {
          bool success = 1;
          string errorMessage = 2;
          string token = 3;
          google.protobuf.Timestamp expiration = 4;
        }
        """
        arg = to_message(clouddrive.pb2.GetTokenRequest, arg)
        if async_:
            return self.async_stub.GetToken(arg, metadata=self.metadata)
        else:
            return self.stub.GetToken(arg, metadata=self.metadata)

    @overload
    def GetUploadFileCount(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetUploadFileCountResult:
        ...
    @overload
    def GetUploadFileCount(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetUploadFileCountResult]:
        ...
    def GetUploadFileCount(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetUploadFileCountResult | Coroutine[Any, Any, clouddrive.pb2.GetUploadFileCountResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetUploadFileCount(google.protobuf.Empty) returns (GetUploadFileCountResult);

        ------------------- protobuf type definition -------------------

        message GetUploadFileCountResult {
          uint32 fileCount = 1;
        }
        """
        if async_:
            return self.async_stub.GetUploadFileCount(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetUploadFileCount(Empty(), metadata=self.metadata)

    @overload
    def GetUploadFileList(
        self, 
        arg: dict | clouddrive.pb2.GetUploadFileListRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.GetUploadFileListResult:
        ...
    @overload
    def GetUploadFileList(
        self, 
        arg: dict | clouddrive.pb2.GetUploadFileListRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.GetUploadFileListResult]:
        ...
    def GetUploadFileList(
        self, 
        arg: dict | clouddrive.pb2.GetUploadFileListRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.GetUploadFileListResult | Coroutine[Any, Any, clouddrive.pb2.GetUploadFileListResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetUploadFileList(GetUploadFileListRequest) returns (GetUploadFileListResult);

        ------------------- protobuf type definition -------------------

        message GetUploadFileListRequest {
          bool getAll = 1;
          uint32 itemsPerPage = 2;
          uint32 pageNumber = 3;
          string filter = 4;
          Status statusFilter = 5;
          OperatorType operatorTypeFilter = 6;
        }
        message GetUploadFileListResult {
          uint32 totalCount = 1;
          repeated UploadFileInfo uploadFiles = 2;
          double globalBytesPerSecond = 3;
          uint64 totalBytes = 4;
          uint64 finishedBytes = 5;
        }
        enum OperatorType {
          OperatorType_Mount = 0;
          OperatorType_Copy = 1;
          OperatorType_BackupFile = 2;
        }
        enum Status {
          Status_Idle = 0;
          Status_WalkingThrough = 1;
          Status_Error = 2;
          Status_Disabled = 3;
          Status_Scanned = 4;
          Status_Finished = 5;
        }
        message UploadFileInfo {
          string key = 1;
          string destPath = 2;
          uint64 size = 3;
          uint64 transferedBytes = 4;
          string status = 5;
          string errorMessage = 6;
          OperatorType operatorType = 7;
          Status statusEnum = 8;
        }
        """
        arg = to_message(clouddrive.pb2.GetUploadFileListRequest, arg)
        if async_:
            return self.async_stub.GetUploadFileList(arg, metadata=self.metadata)
        else:
            return self.stub.GetUploadFileList(arg, metadata=self.metadata)

    @overload
    def GetWebhookConfigTemplate(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.StringResult:
        ...
    @overload
    def GetWebhookConfigTemplate(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        ...
    def GetWebhookConfigTemplate(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.StringResult | Coroutine[Any, Any, clouddrive.pb2.StringResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetWebhookConfigTemplate(google.protobuf.Empty) returns (StringResult);

        ------------------- protobuf type definition -------------------

        message StringResult {
          string result = 1;
        }
        """
        if async_:
            return self.async_stub.GetWebhookConfigTemplate(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetWebhookConfigTemplate(Empty(), metadata=self.metadata)

    @overload
    def GetWebhookConfigs(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.WebhookList:
        ...
    @overload
    def GetWebhookConfigs(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.WebhookList]:
        ...
    def GetWebhookConfigs(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.WebhookList | Coroutine[Any, Any, clouddrive.pb2.WebhookList]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc GetWebhookConfigs(google.protobuf.Empty) returns (WebhookList);

        ------------------- protobuf type definition -------------------

        message WebhookInfo {
          string fileName = 1;
          string content = 2;
          bool isValid = 3;
        }
        message WebhookList {
          repeated WebhookInfo webhooks = 1;
        }
        """
        if async_:
            return self.async_stub.GetWebhookConfigs(Empty(), metadata=self.metadata)
        else:
            return self.stub.GetWebhookConfigs(Empty(), metadata=self.metadata)

    @overload
    def HasDriveLetters(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.HasDriveLettersResult:
        ...
    @overload
    def HasDriveLetters(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.HasDriveLettersResult]:
        ...
    def HasDriveLetters(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.HasDriveLettersResult | Coroutine[Any, Any, clouddrive.pb2.HasDriveLettersResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc HasDriveLetters(google.protobuf.Empty) returns (HasDriveLettersResult);

        ------------------- protobuf type definition -------------------

        message HasDriveLettersResult {
          bool hasDriveLetters = 1;
        }
        """
        if async_:
            return self.async_stub.HasDriveLetters(Empty(), metadata=self.metadata)
        else:
            return self.stub.HasDriveLetters(Empty(), metadata=self.metadata)

    @overload
    def HasUpdate(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.UpdateResult:
        ...
    @overload
    def HasUpdate(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.UpdateResult]:
        ...
    def HasUpdate(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.UpdateResult | Coroutine[Any, Any, clouddrive.pb2.UpdateResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc HasUpdate(google.protobuf.Empty) returns (UpdateResult);

        ------------------- protobuf type definition -------------------

        message UpdateResult {
          bool hasUpdate = 1;
          string newVersion = 2;
          string description = 3;
        }
        """
        if async_:
            return self.async_stub.HasUpdate(Empty(), metadata=self.metadata)
        else:
            return self.stub.HasUpdate(Empty(), metadata=self.metadata)

    @overload
    def JoinPlan(
        self, 
        arg: dict | clouddrive.pb2.JoinPlanRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.JoinPlanResult:
        ...
    @overload
    def JoinPlan(
        self, 
        arg: dict | clouddrive.pb2.JoinPlanRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.JoinPlanResult]:
        ...
    def JoinPlan(
        self, 
        arg: dict | clouddrive.pb2.JoinPlanRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.JoinPlanResult | Coroutine[Any, Any, clouddrive.pb2.JoinPlanResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc JoinPlan(JoinPlanRequest) returns (JoinPlanResult);

        ------------------- protobuf type definition -------------------

        message JoinPlanRequest {
          string planId = 1;
          string couponCode = 2;
        }
        message JoinPlanResult {
          bool success = 1;
          double balance = 2;
          string planName = 3;
          string planDescription = 4;
          google.protobuf.Timestamp expireTime = 5;
          PaymentInfo paymentInfo = 6;
        }
        message PaymentInfo {
          string user_id = 1;
          string plan_id = 2;
          map<string, string> paymentMethods = 3;
          string coupon_code = 4;
          string machine_id = 5;
          string check_code = 6;
        }
        """
        arg = to_message(clouddrive.pb2.JoinPlanRequest, arg)
        if async_:
            return self.async_stub.JoinPlan(arg, metadata=self.metadata)
        else:
            return self.stub.JoinPlan(arg, metadata=self.metadata)

    @overload
    def KickoutDevice(
        self, 
        arg: dict | clouddrive.pb2.DeviceRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def KickoutDevice(
        self, 
        arg: dict | clouddrive.pb2.DeviceRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def KickoutDevice(
        self, 
        arg: dict | clouddrive.pb2.DeviceRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc KickoutDevice(DeviceRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message DeviceRequest {
          string deviceId = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.KickoutDevice(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.KickoutDevice(arg, metadata=self.metadata)
            return None

    @overload
    def ListAllOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.OfflineFileListAllRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OfflineFileListAllResult:
        ...
    @overload
    def ListAllOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.OfflineFileListAllRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OfflineFileListAllResult]:
        ...
    def ListAllOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.OfflineFileListAllRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OfflineFileListAllResult | Coroutine[Any, Any, clouddrive.pb2.OfflineFileListAllResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ListAllOfflineFiles(OfflineFileListAllRequest) returns (OfflineFileListAllResult);

        ------------------- protobuf type definition -------------------

        message OfflineFile {
          string name = 1;
          uint64 size = 2;
          string url = 3;
          OfflineFileStatus status = 4;
          string infoHash = 5;
          string fileId = 6;
          uint64 add_time = 7;
          string parentId = 8;
          double percendDone = 9;
          uint64 peers = 10;
        }
        message OfflineFileListAllRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          uint32 page = 3;
          string path = 4;
        }
        message OfflineFileListAllResult {
          uint32 pageNo = 1;
          uint32 pageRowCount = 2;
          uint32 pageCount = 3;
          uint32 totalCount = 4;
          OfflineStatus status = 5;
          repeated OfflineFile offlineFiles = 6;
        }
        message OfflineStatus {
          uint32 quota = 1;
          uint32 total = 2;
        }
        """
        arg = to_message(clouddrive.pb2.OfflineFileListAllRequest, arg)
        if async_:
            return self.async_stub.ListAllOfflineFiles(arg, metadata=self.metadata)
        else:
            return self.stub.ListAllOfflineFiles(arg, metadata=self.metadata)

    @overload
    def ListLogFiles(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.ListLogFileResult:
        ...
    @overload
    def ListLogFiles(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.ListLogFileResult]:
        ...
    def ListLogFiles(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.ListLogFileResult | Coroutine[Any, Any, clouddrive.pb2.ListLogFileResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ListLogFiles(google.protobuf.Empty) returns (ListLogFileResult);

        ------------------- protobuf type definition -------------------

        message ListLogFileResult {
          repeated LogFileRecord logFiles = 1;
        }
        message LogFileRecord {
          string fileName = 1;
          google.protobuf.Timestamp lastModifiedTime = 2;
          uint64 fileSize = 3;
          string signature = 4;
        }
        """
        if async_:
            return self.async_stub.ListLogFiles(Empty(), metadata=self.metadata)
        else:
            return self.stub.ListLogFiles(Empty(), metadata=self.metadata)

    @overload
    def ListOfflineFilesByPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.OfflineFileListResult:
        ...
    @overload
    def ListOfflineFilesByPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.OfflineFileListResult]:
        ...
    def ListOfflineFilesByPath(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.OfflineFileListResult | Coroutine[Any, Any, clouddrive.pb2.OfflineFileListResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ListOfflineFilesByPath(FileRequest) returns (OfflineFileListResult);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message OfflineFile {
          string name = 1;
          uint64 size = 2;
          string url = 3;
          OfflineFileStatus status = 4;
          string infoHash = 5;
          string fileId = 6;
          uint64 add_time = 7;
          string parentId = 8;
          double percendDone = 9;
          uint64 peers = 10;
        }
        message OfflineFileListResult {
          repeated OfflineFile offlineFiles = 1;
          OfflineStatus status = 2;
        }
        message OfflineStatus {
          uint32 quota = 1;
          uint32 total = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.ListOfflineFilesByPath(arg, metadata=self.metadata)
        else:
            return self.stub.ListOfflineFilesByPath(arg, metadata=self.metadata)

    @overload
    def ListTokens(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.ListTokensResult:
        ...
    @overload
    def ListTokens(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.ListTokensResult]:
        ...
    def ListTokens(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.ListTokensResult | Coroutine[Any, Any, clouddrive.pb2.ListTokensResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ListTokens(google.protobuf.Empty) returns (ListTokensResult);

        ------------------- protobuf type definition -------------------

        message ListTokensResult {
          repeated TokenInfo tokens = 1;
        }
        message TokenInfo {
          string token = 1;
          string rootDir = 2;
          TokenPermissions permissions = 3;
          uint64 expires_in = 4;
          string friendly_name = 5;
        }
        """
        if async_:
            return self.async_stub.ListTokens(Empty(), metadata=self.metadata)
        else:
            return self.stub.ListTokens(Empty(), metadata=self.metadata)

    @overload
    def LocalGetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.LocalGetSubFilesRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.LocalGetSubFilesResult]:
        ...
    @overload
    def LocalGetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.LocalGetSubFilesRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.LocalGetSubFilesResult]]:
        ...
    def LocalGetSubFiles(
        self, 
        arg: dict | clouddrive.pb2.LocalGetSubFilesRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.LocalGetSubFilesResult] | Coroutine[Any, Any, Iterable[clouddrive.pb2.LocalGetSubFilesResult]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc LocalGetSubFiles(LocalGetSubFilesRequest) returns (stream LocalGetSubFilesResult);

        ------------------- protobuf type definition -------------------

        message LocalGetSubFilesRequest {
          string parentFolder = 1;
          bool folderOnly = 2;
          bool includeCloudDrive = 3;
          bool includeAvailableDrive = 4;
        }
        message LocalGetSubFilesResult {
          repeated string subFiles = 1;
        }
        """
        arg = to_message(clouddrive.pb2.LocalGetSubFilesRequest, arg)
        if async_:
            return self.async_stub.LocalGetSubFiles(arg, metadata=self.metadata)
        else:
            return self.stub.LocalGetSubFiles(arg, metadata=self.metadata)

    @overload
    def LockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def LockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def LockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc LockEncryptedFile(FileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.LockEncryptedFile(arg, metadata=self.metadata)
        else:
            return self.stub.LockEncryptedFile(arg, metadata=self.metadata)

    @overload
    def Login(
        self, 
        arg: dict | clouddrive.pb2.UserLoginRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def Login(
        self, 
        arg: dict | clouddrive.pb2.UserLoginRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def Login(
        self, 
        arg: dict | clouddrive.pb2.UserLoginRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc Login(UserLoginRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message UserLoginRequest {
          string userName = 1;
          string password = 2;
          bool synDataToCloud = 3;
        }
        """
        arg = to_message(clouddrive.pb2.UserLoginRequest, arg)
        if async_:
            return self.async_stub.Login(arg, metadata=self.metadata)
        else:
            return self.stub.Login(arg, metadata=self.metadata)

    @overload
    def Logout(
        self, 
        arg: dict | clouddrive.pb2.UserLogoutRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def Logout(
        self, 
        arg: dict | clouddrive.pb2.UserLogoutRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def Logout(
        self, 
        arg: dict | clouddrive.pb2.UserLogoutRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc Logout(UserLogoutRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message UserLogoutRequest {
          bool logoutFromCloudFS = 1;
        }
        """
        arg = to_message(clouddrive.pb2.UserLogoutRequest, arg)
        if async_:
            return self.async_stub.Logout(arg, metadata=self.metadata)
        else:
            return self.stub.Logout(arg, metadata=self.metadata)

    @overload
    def ModifyDavUser(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavUserRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ModifyDavUser(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavUserRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ModifyDavUser(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavUserRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ModifyDavUser(ModifyDavUserRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ModifyDavUserRequest {
          string userName = 1;
          string password = 2;
          string rootPath = 3;
          bool readOnly = 4;
          bool enabled = 5;
          bool guest = 6;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ModifyDavUser(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ModifyDavUser(arg, metadata=self.metadata)
            return None

    @overload
    def ModifyToken(
        self, 
        arg: dict | clouddrive.pb2.ModifyTokenRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.TokenInfo:
        ...
    @overload
    def ModifyToken(
        self, 
        arg: dict | clouddrive.pb2.ModifyTokenRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        ...
    def ModifyToken(
        self, 
        arg: dict | clouddrive.pb2.ModifyTokenRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.TokenInfo | Coroutine[Any, Any, clouddrive.pb2.TokenInfo]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ModifyToken(ModifyTokenRequest) returns (TokenInfo);

        ------------------- protobuf type definition -------------------

        message ModifyTokenRequest {
          string token = 1;
          string rootDir = 2;
          TokenPermissions permissions = 3;
          string friendly_name = 4;
          uint64 expires_in = 5;
        }
        message TokenInfo {
          string token = 1;
          string rootDir = 2;
          TokenPermissions permissions = 3;
          uint64 expires_in = 4;
          string friendly_name = 5;
        }
        message TokenPermissions {
          bool allow_list = 1;
          bool allow_search = 2;
          bool allow_list_local = 3;
          bool allow_create_folder = 4;
          bool allow_create_file = 5;
          bool allow_write = 6;
          bool allow_read = 7;
          bool allow_rename = 8;
          bool allow_move = 9;
          bool allow_copy = 10;
          bool allow_delete = 11;
          bool allow_delete_permanently = 12;
          bool allow_create_encrypt = 13;
          bool allow_unlock_encrypted = 14;
          bool allow_lock_encrypted = 15;
          bool allow_add_offline_download = 16;
          bool allow_list_offline_downloads = 17;
          bool allow_modify_offline_downloads = 18;
          bool allow_shared_links = 19;
          bool allow_view_properties = 20;
          bool allow_get_space_info = 21;
          bool allow_view_runtime_info = 22;
          bool allow_get_memberships = 23;
          bool allow_modify_memberships = 24;
          bool allow_get_mounts = 25;
          bool allow_modify_mounts = 26;
          bool allow_get_transfer_tasks = 27;
          bool allow_modify_transfer_tasks = 28;
          bool allow_get_cloud_apis = 29;
          bool allow_modify_cloud_apis = 30;
          bool allow_get_system_settings = 31;
          bool allow_modify_system_settings = 32;
          bool allow_get_backups = 33;
          bool allow_modify_backups = 34;
          bool allow_get_dav_config = 35;
          bool allow_modify_dav_config = 36;
          bool allow_token_management = 37;
          bool allow_get_account_info = 38;
          bool allow_modify_account = 39;
          bool allow_service_control = 40;
        }
        """
        arg = to_message(clouddrive.pb2.ModifyTokenRequest, arg)
        if async_:
            return self.async_stub.ModifyToken(arg, metadata=self.metadata)
        else:
            return self.stub.ModifyToken(arg, metadata=self.metadata)

    @overload
    def Mount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.MountPointResult:
        ...
    @overload
    def Mount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        ...
    def Mount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.MountPointResult | Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc Mount(MountPointRequest) returns (MountPointResult);

        ------------------- protobuf type definition -------------------

        message MountPointRequest {
          string MountPoint = 1;
        }
        message MountPointResult {
          bool success = 1;
          string failReason = 2;
        }
        """
        arg = to_message(clouddrive.pb2.MountPointRequest, arg)
        if async_:
            return self.async_stub.Mount(arg, metadata=self.metadata)
        else:
            return self.stub.Mount(arg, metadata=self.metadata)

    @overload
    def MoveFile(
        self, 
        arg: dict | clouddrive.pb2.MoveFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def MoveFile(
        self, 
        arg: dict | clouddrive.pb2.MoveFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def MoveFile(
        self, 
        arg: dict | clouddrive.pb2.MoveFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc MoveFile(MoveFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        enum ConflictPolicy {
          ConflictPolicy_Overwrite = 0;
          ConflictPolicy_Rename = 1;
          ConflictPolicy_Skip = 2;
        }
        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message MoveFileRequest {
          repeated string theFilePaths = 1;
          string destPath = 2;
          ConflictPolicy conflictPolicy = 3;
          bool moveAcrossClouds = 4;
          bool handleConflictRecursively = 5;
        }
        """
        arg = to_message(clouddrive.pb2.MoveFileRequest, arg)
        if async_:
            return self.async_stub.MoveFile(arg, metadata=self.metadata)
        else:
            return self.stub.MoveFile(arg, metadata=self.metadata)

    @overload
    def PauseAllCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseAllCopyTasksRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def PauseAllCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseAllCopyTasksRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def PauseAllCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseAllCopyTasksRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PauseAllCopyTasks(PauseAllCopyTasksRequest) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        message PauseAllCopyTasksRequest {
          bool pause = 1;
        }
        """
        arg = to_message(clouddrive.pb2.PauseAllCopyTasksRequest, arg)
        if async_:
            return self.async_stub.PauseAllCopyTasks(arg, metadata=self.metadata)
        else:
            return self.stub.PauseAllCopyTasks(arg, metadata=self.metadata)

    @overload
    def PauseAllUploadFiles(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def PauseAllUploadFiles(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def PauseAllUploadFiles(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PauseAllUploadFiles(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.PauseAllUploadFiles(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.PauseAllUploadFiles(Empty(), metadata=self.metadata)
            return None

    @overload
    def PauseCopyTask(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTaskRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def PauseCopyTask(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTaskRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def PauseCopyTask(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTaskRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PauseCopyTask(PauseCopyTaskRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message PauseCopyTaskRequest {
          string sourcePath = 1;
          string destPath = 2;
          bool pause = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.PauseCopyTask(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.PauseCopyTask(arg, metadata=self.metadata)
            return None

    @overload
    def PauseCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTasksRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def PauseCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTasksRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def PauseCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.PauseCopyTasksRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PauseCopyTasks(PauseCopyTasksRequest) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        message PauseCopyTasksRequest {
          repeated string taskKeys = 1;
          bool pause = 2;
        }
        """
        arg = to_message(clouddrive.pb2.PauseCopyTasksRequest, arg)
        if async_:
            return self.async_stub.PauseCopyTasks(arg, metadata=self.metadata)
        else:
            return self.stub.PauseCopyTasks(arg, metadata=self.metadata)

    @overload
    def PauseUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def PauseUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def PauseUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PauseUploadFiles(MultpleUploadFileKeyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message MultpleUploadFileKeyRequest {
          repeated string keys = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.PauseUploadFiles(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.PauseUploadFiles(arg, metadata=self.metadata)
            return None

    @overload
    def PushMessage(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.CloudDrivePushMessage]:
        ...
    @overload
    def PushMessage(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.CloudDrivePushMessage]]:
        ...
    def PushMessage(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.CloudDrivePushMessage] | Coroutine[Any, Any, Iterable[clouddrive.pb2.CloudDrivePushMessage]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PushMessage(google.protobuf.Empty) returns (stream CloudDrivePushMessage);

        ------------------- protobuf type definition -------------------

        message CloudDrivePushMessage {
          MessageType messageType = 1;
          TransferTaskStatus transferTaskStatus = 2;
          UpdateStatus updateStatus = 3;
          ExitedMessage exitedMessage = 4;
          FileSystemChange fileSystemChange = 5;
          MountPointChange mountPointChange = 6;
          LogMessage logMessage = 7;
          MergeTaskUpdate mergeTaskUpdate = 8;
        }
        message ExitedMessage {
          ExitReason exitReason = 1;
          string message = 2;
        }
        message FileSystemChange {
          ChangeType changeType = 1;
          bool isDirectory = 2;
          string path = 3;
          string newPath = 4;
          CloudDriveFile theFile = 5;
        }
        message LogMessage {
          LogLevel level = 1;
          string message = 2;
          string target = 3;
          google.protobuf.Timestamp timestamp = 4;
          map<string, string> fields = 6;
        }
        message MergeTaskUpdate {
          repeated MergeTask mergeTasks = 1;
          string lastMergedPath = 2;
          string lastMergedNewPath = 3;
        }
        enum MessageType {
          MessageType_DOWNLOADER_COUNT = 0;
          MessageType_UPLOADER_COUNT = 1;
          MessageType_UPDATE_STATUS = 2;
          MessageType_FORCE_EXIT = 3;
          MessageType_FILE_SYSTEM_CHANGE = 4;
          MessageType_MOUNT_POINT_CHANGE = 5;
          MessageType_COPY_TASK_COUNT = 6;
          MessageType_LOG_MESSAGE = 7;
          MessageType_MERGE_TASKS = 8;
        }
        message MountPointChange {
          ActionType actionType = 1;
          string mountPoint = 2;
          bool success = 3;
          string failReason = 4;
        }
        message TransferTaskStatus {
          uint32 downloadCount = 1;
          uint32 uploadCount = 2;
          string clouddriveVersion = 3;
          repeated UploadFileInfo uploadFileStatusChanges = 4;
          bool hasUpdate = 5;
          uint32 copyTaskCount = 6;
        }
        message UpdateStatus {
          UpdatePhase updatePhase = 1;
          string newVersion = 2;
          string message = 3;
          string clouddriveVersion = 4;
          uint64 downloadedBytes = 5;
          uint64 totalBytes = 6;
        }
        """
        if async_:
            return self.async_stub.PushMessage(Empty(), metadata=self.metadata)
        else:
            return self.stub.PushMessage(Empty(), metadata=self.metadata)

    @overload
    def PushTaskChange(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.GetAllTasksCountResult]:
        ...
    @overload
    def PushTaskChange(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.GetAllTasksCountResult]]:
        ...
    def PushTaskChange(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.GetAllTasksCountResult] | Coroutine[Any, Any, Iterable[clouddrive.pb2.GetAllTasksCountResult]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc PushTaskChange(google.protobuf.Empty) returns (stream GetAllTasksCountResult);

        ------------------- protobuf type definition -------------------

        message GetAllTasksCountResult {
          uint32 downloadCount = 1;
          uint32 uploadCount = 2;
          uint32 copyTaskCount = 6;
          PushMessage pushMessage = 3;
          bool hasUpdate = 4;
          repeated UploadFileInfo uploadFileStatusChanges = 5;
        }
        message PushMessage {
          string clouddriveVersion = 1;
        }
        message UploadFileInfo {
          string key = 1;
          string destPath = 2;
          uint64 size = 3;
          uint64 transferedBytes = 4;
          string status = 5;
          string errorMessage = 6;
          OperatorType operatorType = 7;
          Status statusEnum = 8;
        }
        """
        if async_:
            return self.async_stub.PushTaskChange(Empty(), metadata=self.metadata)
        else:
            return self.stub.PushTaskChange(Empty(), metadata=self.metadata)

    @overload
    def Register(
        self, 
        arg: dict | clouddrive.pb2.UserRegisterRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def Register(
        self, 
        arg: dict | clouddrive.pb2.UserRegisterRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def Register(
        self, 
        arg: dict | clouddrive.pb2.UserRegisterRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc Register(UserRegisterRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message UserRegisterRequest {
          string userName = 1;
          string password = 2;
        }
        """
        arg = to_message(clouddrive.pb2.UserRegisterRequest, arg)
        if async_:
            return self.async_stub.Register(arg, metadata=self.metadata)
        else:
            return self.stub.Register(arg, metadata=self.metadata)

    @overload
    def RemoteUploadStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.RemoteEntryRequest], 
        /, 
        async_: Literal[False] = False, 
    ) -> Iterable[clouddrive.pb2.RemoteEntryResponse]:
        ...
    @overload
    def RemoteUploadStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.RemoteEntryRequest], 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, Iterable[clouddrive.pb2.RemoteEntryResponse]]:
        ...
    def RemoteUploadStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.RemoteEntryRequest], 
        /, 
        async_: Literal[False, True] = False, 
    ) -> Iterable[clouddrive.pb2.RemoteEntryResponse] | Coroutine[Any, Any, Iterable[clouddrive.pb2.RemoteEntryResponse]]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoteUploadStream(stream RemoteEntryRequest) returns (stream RemoteEntryResponse);

        ------------------- protobuf type definition -------------------

        message CloseRequest {
        }
        message CloseResponse {
        }
        message GetHashRequest {
          HashType hashType = 1;
        }
        message GetHashResponse {
          string hashValue = 1;
        }
        message GetInfoRequest {
        }
        message GetInfoResponse {
          string name = 1;
          uint64 size = 2;
          bool isDirectory = 3;
          google.protobuf.Timestamp createTime = 4;
          google.protobuf.Timestamp writeTime = 5;
          google.protobuf.Timestamp accessTime = 6;
        }
        message InitRequest {
          string entryPath = 1;
          uint64 fileSize = 2;
          map<uint32, string> knownHashes = 3;
        }
        message InitResponse {
          string entryId = 1;
        }
        message RapidUploadRequest {
          string fileName = 1;
          uint64 fileSize = 2;
        }
        message RapidUploadResponse {
          RapidUploadSuccess success = 1;
          RapidUploadErrorResult rapidError = 2;
          string otherErrorMessage = 3;
          Status status = 4;
        }
        message ReadDataRequest {
          uint64 offset = 1;
          uint64 length = 2;
          bool lazyRead = 3;
        }
        message ReadDataResponse {
          bytes data = 1;
          uint64 bytesRead = 2;
        }
        message RemoteEntryRequest {
          string sessionId = 1;
          InitRequest init = 2;
          GetInfoRequest getInfo = 3;
          GetHashRequest getHash = 4;
          ReadDataResponse readData = 5;
          RapidUploadRequest rapidUpload = 6;
          UploadRequest upload = 7;
          CloseRequest close = 8;
        }
        message RemoteEntryResponse {
          string sessionId = 1;
          bool success = 2;
          string errorMessage = 3;
          InitResponse init = 4;
          GetInfoResponse getInfo = 5;
          GetHashResponse getHash = 6;
          ReadDataRequest readData = 7;
          RapidUploadResponse rapidUpload = 8;
          UploadResponse upload = 9;
          CloseResponse close = 10;
        }
        message UploadRequest {
          string fileName = 1;
          uint64 fileSize = 2;
          string parentPath = 3;
          bytes data = 4;
          uint64 offset = 5;
          bool isLastChunk = 6;
        }
        message UploadResponse {
          uint64 bytesReceived = 1;
          string fileId = 2;
          bool uploadComplete = 3;
          string errorMessage = 4;
          Status status = 5;
        }
        """
        arg = [to_message(clouddrive.pb2.RemoteEntryRequest, a) for a in arg]
        if async_:
            return self.async_stub.RemoteUploadStream(arg, metadata=self.metadata)
        else:
            return self.stub.RemoteUploadStream(arg, metadata=self.metadata)

    @overload
    def RemoveAllCopyTasks(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def RemoveAllCopyTasks(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def RemoveAllCopyTasks(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveAllCopyTasks(google.protobuf.Empty) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        """
        if async_:
            return self.async_stub.RemoveAllCopyTasks(Empty(), metadata=self.metadata)
        else:
            return self.stub.RemoveAllCopyTasks(Empty(), metadata=self.metadata)

    @overload
    def RemoveCloudAPI(
        self, 
        arg: dict | clouddrive.pb2.RemoveCloudAPIRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def RemoveCloudAPI(
        self, 
        arg: dict | clouddrive.pb2.RemoveCloudAPIRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def RemoveCloudAPI(
        self, 
        arg: dict | clouddrive.pb2.RemoveCloudAPIRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveCloudAPI(RemoveCloudAPIRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message RemoveCloudAPIRequest {
          string cloudName = 1;
          string userName = 2;
          bool permanentRemove = 3;
        }
        """
        arg = to_message(clouddrive.pb2.RemoveCloudAPIRequest, arg)
        if async_:
            return self.async_stub.RemoveCloudAPI(arg, metadata=self.metadata)
        else:
            return self.stub.RemoveCloudAPI(arg, metadata=self.metadata)

    @overload
    def RemoveCompletedCopyTasks(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RemoveCompletedCopyTasks(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RemoveCompletedCopyTasks(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveCompletedCopyTasks(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.RemoveCompletedCopyTasks(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RemoveCompletedCopyTasks(Empty(), metadata=self.metadata)
            return None

    @overload
    def RemoveCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def RemoveCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def RemoveCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveCopyTasks(CopyTaskBatchRequest) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        message CopyTaskBatchRequest {
          repeated string taskKeys = 1;
        }
        """
        arg = to_message(clouddrive.pb2.CopyTaskBatchRequest, arg)
        if async_:
            return self.async_stub.RemoveCopyTasks(arg, metadata=self.metadata)
        else:
            return self.stub.RemoveCopyTasks(arg, metadata=self.metadata)

    @overload
    def RemoveDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RemoveDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RemoveDavUser(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveDavUser(StringValue) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.RemoveDavUser(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RemoveDavUser(arg, metadata=self.metadata)
            return None

    @overload
    def RemoveMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.MountPointResult:
        ...
    @overload
    def RemoveMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        ...
    def RemoveMountPoint(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.MountPointResult | Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveMountPoint(MountPointRequest) returns (MountPointResult);

        ------------------- protobuf type definition -------------------

        message MountPointRequest {
          string MountPoint = 1;
        }
        message MountPointResult {
          bool success = 1;
          string failReason = 2;
        }
        """
        arg = to_message(clouddrive.pb2.MountPointRequest, arg)
        if async_:
            return self.async_stub.RemoveMountPoint(arg, metadata=self.metadata)
        else:
            return self.stub.RemoveMountPoint(arg, metadata=self.metadata)

    @overload
    def RemoveOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.RemoveOfflineFilesRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def RemoveOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.RemoveOfflineFilesRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def RemoveOfflineFiles(
        self, 
        arg: dict | clouddrive.pb2.RemoveOfflineFilesRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveOfflineFiles(RemoveOfflineFilesRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message RemoveOfflineFilesRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          bool deleteFiles = 3;
          repeated string infoHashes = 4;
          string path = 5;
        }
        """
        arg = to_message(clouddrive.pb2.RemoveOfflineFilesRequest, arg)
        if async_:
            return self.async_stub.RemoveOfflineFiles(arg, metadata=self.metadata)
        else:
            return self.stub.RemoveOfflineFiles(arg, metadata=self.metadata)

    @overload
    def RemoveToken(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RemoveToken(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RemoveToken(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveToken(StringValue) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.RemoveToken(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RemoveToken(arg, metadata=self.metadata)
            return None

    @overload
    def RemoveWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RemoveWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RemoveWebhookConfig(
        self, 
        arg: dict | clouddrive.pb2.StringValue, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RemoveWebhookConfig(StringValue) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message StringValue {
          string value = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.RemoveWebhookConfig(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RemoveWebhookConfig(arg, metadata=self.metadata)
            return None

    @overload
    def RenameFile(
        self, 
        arg: dict | clouddrive.pb2.RenameFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def RenameFile(
        self, 
        arg: dict | clouddrive.pb2.RenameFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def RenameFile(
        self, 
        arg: dict | clouddrive.pb2.RenameFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RenameFile(RenameFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message RenameFileRequest {
          string theFilePath = 1;
          string newName = 2;
        }
        """
        arg = to_message(clouddrive.pb2.RenameFileRequest, arg)
        if async_:
            return self.async_stub.RenameFile(arg, metadata=self.metadata)
        else:
            return self.stub.RenameFile(arg, metadata=self.metadata)

    @overload
    def RenameFiles(
        self, 
        arg: dict | clouddrive.pb2.RenameFilesRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def RenameFiles(
        self, 
        arg: dict | clouddrive.pb2.RenameFilesRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def RenameFiles(
        self, 
        arg: dict | clouddrive.pb2.RenameFilesRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RenameFiles(RenameFilesRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message RenameFileRequest {
          string theFilePath = 1;
          string newName = 2;
        }
        message RenameFilesRequest {
          repeated RenameFileRequest renameFiles = 1;
        }
        """
        arg = to_message(clouddrive.pb2.RenameFilesRequest, arg)
        if async_:
            return self.async_stub.RenameFiles(arg, metadata=self.metadata)
        else:
            return self.stub.RenameFiles(arg, metadata=self.metadata)

    @overload
    def ResetAccount(
        self, 
        arg: dict | clouddrive.pb2.ResetAccountRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ResetAccount(
        self, 
        arg: dict | clouddrive.pb2.ResetAccountRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ResetAccount(
        self, 
        arg: dict | clouddrive.pb2.ResetAccountRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ResetAccount(ResetAccountRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ResetAccountRequest {
          string resetCode = 1;
          string newPassword = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ResetAccount(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ResetAccount(arg, metadata=self.metadata)
            return None

    @overload
    def RestartCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RestartCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RestartCopyTask(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RestartCopyTask(CopyTaskRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message CopyTaskRequest {
          string sourcePath = 1;
          string destPath = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.RestartCopyTask(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RestartCopyTask(arg, metadata=self.metadata)
            return None

    @overload
    def RestartOfflineTask(
        self, 
        arg: dict | clouddrive.pb2.RestartOfflineFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RestartOfflineTask(
        self, 
        arg: dict | clouddrive.pb2.RestartOfflineFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RestartOfflineTask(
        self, 
        arg: dict | clouddrive.pb2.RestartOfflineFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RestartOfflineTask(RestartOfflineFileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message RestartOfflineFileRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          string infoHash = 3;
          string url = 4;
          string parentId = 5;
          string path = 6;
        }
        """
        if async_:
            async def request():
                await self.async_stub.RestartOfflineTask(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RestartOfflineTask(arg, metadata=self.metadata)
            return None

    @overload
    def RestartService(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def RestartService(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def RestartService(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc RestartService(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.RestartService(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.RestartService(Empty(), metadata=self.metadata)
            return None

    @overload
    def ResumeAllCopyTasks(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def ResumeAllCopyTasks(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def ResumeAllCopyTasks(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ResumeAllCopyTasks(google.protobuf.Empty) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        """
        if async_:
            return self.async_stub.ResumeAllCopyTasks(Empty(), metadata=self.metadata)
        else:
            return self.stub.ResumeAllCopyTasks(Empty(), metadata=self.metadata)

    @overload
    def ResumeAllUploadFiles(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ResumeAllUploadFiles(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ResumeAllUploadFiles(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ResumeAllUploadFiles(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.ResumeAllUploadFiles(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ResumeAllUploadFiles(Empty(), metadata=self.metadata)
            return None

    @overload
    def ResumeCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.BatchOperationResult:
        ...
    @overload
    def ResumeCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        ...
    def ResumeCopyTasks(
        self, 
        arg: dict | clouddrive.pb2.CopyTaskBatchRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.BatchOperationResult | Coroutine[Any, Any, clouddrive.pb2.BatchOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ResumeCopyTasks(CopyTaskBatchRequest) returns (BatchOperationResult);

        ------------------- protobuf type definition -------------------

        message BatchOperationResult {
          bool success = 1;
          uint32 affectedCount = 2;
          string errorMessage = 3;
        }
        message CopyTaskBatchRequest {
          repeated string taskKeys = 1;
        }
        """
        arg = to_message(clouddrive.pb2.CopyTaskBatchRequest, arg)
        if async_:
            return self.async_stub.ResumeCopyTasks(arg, metadata=self.metadata)
        else:
            return self.stub.ResumeCopyTasks(arg, metadata=self.metadata)

    @overload
    def ResumeUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ResumeUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ResumeUploadFiles(
        self, 
        arg: dict | clouddrive.pb2.MultpleUploadFileKeyRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ResumeUploadFiles(MultpleUploadFileKeyRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message MultpleUploadFileKeyRequest {
          repeated string keys = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.ResumeUploadFiles(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ResumeUploadFiles(arg, metadata=self.metadata)
            return None

    @overload
    def SendChangeEmailCode(
        self, 
        arg: dict | clouddrive.pb2.SendChangeEmailCodeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SendChangeEmailCode(
        self, 
        arg: dict | clouddrive.pb2.SendChangeEmailCodeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SendChangeEmailCode(
        self, 
        arg: dict | clouddrive.pb2.SendChangeEmailCodeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SendChangeEmailCode(SendChangeEmailCodeRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message SendChangeEmailCodeRequest {
          string newEmail = 1;
          string password = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SendChangeEmailCode(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SendChangeEmailCode(arg, metadata=self.metadata)
            return None

    @overload
    def SendConfirmEmail(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SendConfirmEmail(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SendConfirmEmail(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SendConfirmEmail(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.SendConfirmEmail(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SendConfirmEmail(Empty(), metadata=self.metadata)
            return None

    @overload
    def SendPromotionAction(
        self, 
        arg: dict | clouddrive.pb2.SendPromotionActionRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SendPromotionAction(
        self, 
        arg: dict | clouddrive.pb2.SendPromotionActionRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SendPromotionAction(
        self, 
        arg: dict | clouddrive.pb2.SendPromotionActionRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SendPromotionAction(SendPromotionActionRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message SendPromotionActionRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          string promotionId = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SendPromotionAction(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SendPromotionAction(arg, metadata=self.metadata)
            return None

    @overload
    def SendResetAccountEmail(
        self, 
        arg: dict | clouddrive.pb2.SendResetAccountEmailRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SendResetAccountEmail(
        self, 
        arg: dict | clouddrive.pb2.SendResetAccountEmailRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SendResetAccountEmail(
        self, 
        arg: dict | clouddrive.pb2.SendResetAccountEmailRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SendResetAccountEmail(SendResetAccountEmailRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message SendResetAccountEmailRequest {
          string email = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SendResetAccountEmail(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SendResetAccountEmail(arg, metadata=self.metadata)
            return None

    @overload
    def SetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.SetCloudAPIConfigRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.SetCloudAPIConfigRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SetCloudAPIConfig(
        self, 
        arg: dict | clouddrive.pb2.SetCloudAPIConfigRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SetCloudAPIConfig(SetCloudAPIConfigRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message CloudAPIConfig {
          uint32 maxDownloadThreads = 1;
          uint64 minReadLengthKB = 2;
          uint64 maxReadLengthKB = 3;
          uint64 defaultReadLengthKB = 4;
          uint64 maxBufferPoolSizeMB = 5;
          double maxQueriesPerSecond = 6;
          bool forceIpv4 = 7;
          ProxyInfo apiProxy = 8;
          ProxyInfo dataProxy = 9;
          string customUserAgent = 10;
          uint32 maxUploadThreads = 11;
          bool insecureTls = 12;
        }
        message SetCloudAPIConfigRequest {
          string cloudName = 1;
          string userName = 2;
          CloudAPIConfig config = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SetCloudAPIConfig(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SetCloudAPIConfig(arg, metadata=self.metadata)
            return None

    @overload
    def SetDavServerConfig(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavServerConfigRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SetDavServerConfig(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavServerConfigRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SetDavServerConfig(
        self, 
        arg: dict | clouddrive.pb2.ModifyDavServerConfigRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SetDavServerConfig(ModifyDavServerConfigRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message ModifyDavServerConfigRequest {
          bool enableDavServer = 1;
          bool enableClouddriveAccount = 2;
          string clouddriveAccountRootPath = 3;
          bool clouddriveAccountReadOnly = 4;
          bool enableAnonymousAccess = 5;
          string anonymousRootPath = 6;
          bool anonymousReadOnly = 7;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SetDavServerConfig(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SetDavServerConfig(arg, metadata=self.metadata)
            return None

    @overload
    def SetDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.SetDirCacheTimeRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SetDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.SetDirCacheTimeRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SetDirCacheTimeSecs(
        self, 
        arg: dict | clouddrive.pb2.SetDirCacheTimeRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SetDirCacheTimeSecs(SetDirCacheTimeRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message SetDirCacheTimeRequest {
          string path = 1;
          uint64 dirCachTimeToLiveSecs = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SetDirCacheTimeSecs(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SetDirCacheTimeSecs(arg, metadata=self.metadata)
            return None

    @overload
    def SetSystemSettings(
        self, 
        arg: dict | clouddrive.pb2.SystemSettings, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def SetSystemSettings(
        self, 
        arg: dict | clouddrive.pb2.SystemSettings, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def SetSystemSettings(
        self, 
        arg: dict | clouddrive.pb2.SystemSettings, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SetSystemSettings(SystemSettings) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        enum LogLevel {
          LogLevel_Trace = 0;
          LogLevel_Debug = 1;
          LogLevel_Info = 2;
          LogLevel_Warn = 3;
          LogLevel_Error = 4;
        }
        message ProxyInfo {
          ProxyType proxyType = 1;
          string host = 2;
          uint32 port = 3;
          string username = 4;
          string password = 5;
        }
        message StringList {
          repeated string values = 1;
        }
        message SystemSettings {
          uint64 dirCacheTimeToLiveSecs = 1;
          uint64 maxPreProcessTasks = 2;
          uint64 maxProcessTasks = 3;
          string tempFileLocation = 4;
          bool syncWithCloud = 5;
          uint64 readDownloaderTimeoutSecs = 6;
          uint64 uploadDelaySecs = 7;
          StringList processBlackList = 8;
          StringList uploadIgnoredExtensions = 9;
          UpdateChannel updateChannel = 10;
          double maxDownloadSpeedKBytesPerSecond = 11;
          double maxUploadSpeedKBytesPerSecond = 12;
          string deviceName = 13;
          bool dirCachePersistence = 14;
          string dirCacheDbLocation = 15;
          LogLevel fileLogLevel = 16;
          LogLevel terminalLogLevel = 17;
          LogLevel backupLogLevel = 18;
          bool EnableAutoRegisterDevice = 19;
          LogLevel realtimeLogLevel = 20;
          StringList operatorPriorityOrder = 21;
          ProxyInfo updateProxy = 22;
        }
        enum UpdateChannel {
          UpdateChannel_Release = 0;
          UpdateChannel_Beta = 1;
        }
        """
        if async_:
            async def request():
                await self.async_stub.SetSystemSettings(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.SetSystemSettings(arg, metadata=self.metadata)
            return None

    @overload
    def ShutdownService(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def ShutdownService(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def ShutdownService(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc ShutdownService(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.ShutdownService(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.ShutdownService(Empty(), metadata=self.metadata)
            return None

    @overload
    def StartCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def StartCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def StartCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc StartCloudEventListener(FileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.StartCloudEventListener(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.StartCloudEventListener(arg, metadata=self.metadata)
            return None

    @overload
    def StopCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def StopCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def StopCloudEventListener(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc StopCloudEventListener(FileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.StopCloudEventListener(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.StopCloudEventListener(arg, metadata=self.metadata)
            return None

    @overload
    def SyncFileChangesFromCloud(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileSystemChangeStatistics:
        ...
    @overload
    def SyncFileChangesFromCloud(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileSystemChangeStatistics]:
        ...
    def SyncFileChangesFromCloud(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileSystemChangeStatistics | Coroutine[Any, Any, clouddrive.pb2.FileSystemChangeStatistics]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc SyncFileChangesFromCloud(FileRequest) returns (FileSystemChangeStatistics);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message FileSystemChangeStatistics {
          uint64 createCount = 1;
          uint64 deleteCount = 2;
          uint64 renameCount = 3;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.SyncFileChangesFromCloud(arg, metadata=self.metadata)
        else:
            return self.stub.SyncFileChangesFromCloud(arg, metadata=self.metadata)

    @overload
    def TestUpdate(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def TestUpdate(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def TestUpdate(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc TestUpdate(FileRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        """
        if async_:
            async def request():
                await self.async_stub.TestUpdate(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.TestUpdate(arg, metadata=self.metadata)
            return None

    @overload
    def TransferBalance(
        self, 
        arg: dict | clouddrive.pb2.TransferBalanceRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def TransferBalance(
        self, 
        arg: dict | clouddrive.pb2.TransferBalanceRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def TransferBalance(
        self, 
        arg: dict | clouddrive.pb2.TransferBalanceRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc TransferBalance(TransferBalanceRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message TransferBalanceRequest {
          string toUserName = 1;
          double amount = 2;
          string password = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.TransferBalance(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.TransferBalance(arg, metadata=self.metadata)
            return None

    @overload
    def UnlockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.UnlockEncryptedFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.FileOperationResult:
        ...
    @overload
    def UnlockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.UnlockEncryptedFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        ...
    def UnlockEncryptedFile(
        self, 
        arg: dict | clouddrive.pb2.UnlockEncryptedFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.FileOperationResult | Coroutine[Any, Any, clouddrive.pb2.FileOperationResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc UnlockEncryptedFile(UnlockEncryptedFileRequest) returns (FileOperationResult);

        ------------------- protobuf type definition -------------------

        message FileOperationResult {
          bool success = 1;
          string errorMessage = 2;
          repeated string resultFilePaths = 3;
        }
        message UnlockEncryptedFileRequest {
          string path = 1;
          string password = 2;
          bool permanentUnlock = 3;
        }
        """
        arg = to_message(clouddrive.pb2.UnlockEncryptedFileRequest, arg)
        if async_:
            return self.async_stub.UnlockEncryptedFile(arg, metadata=self.metadata)
        else:
            return self.stub.UnlockEncryptedFile(arg, metadata=self.metadata)

    @overload
    def Unmount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.MountPointResult:
        ...
    @overload
    def Unmount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        ...
    def Unmount(
        self, 
        arg: dict | clouddrive.pb2.MountPointRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.MountPointResult | Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc Unmount(MountPointRequest) returns (MountPointResult);

        ------------------- protobuf type definition -------------------

        message MountPointRequest {
          string MountPoint = 1;
        }
        message MountPointResult {
          bool success = 1;
          string failReason = 2;
        }
        """
        arg = to_message(clouddrive.pb2.MountPointRequest, arg)
        if async_:
            return self.async_stub.Unmount(arg, metadata=self.metadata)
        else:
            return self.stub.Unmount(arg, metadata=self.metadata)

    @overload
    def UpdateMountPoint(
        self, 
        arg: dict | clouddrive.pb2.UpdateMountPointRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.MountPointResult:
        ...
    @overload
    def UpdateMountPoint(
        self, 
        arg: dict | clouddrive.pb2.UpdateMountPointRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        ...
    def UpdateMountPoint(
        self, 
        arg: dict | clouddrive.pb2.UpdateMountPointRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.MountPointResult | Coroutine[Any, Any, clouddrive.pb2.MountPointResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc UpdateMountPoint(UpdateMountPointRequest) returns (MountPointResult);

        ------------------- protobuf type definition -------------------

        message MountOption {
          string mountPoint = 1;
          string sourceDir = 2;
          bool localMount = 3;
          bool readOnly = 4;
          bool autoMount = 5;
          uint32 uid = 6;
          uint32 gid = 7;
          string permissions = 8;
          string name = 9;
        }
        message MountPointResult {
          bool success = 1;
          string failReason = 2;
        }
        message UpdateMountPointRequest {
          string mountPoint = 1;
          MountOption newMountOption = 2;
        }
        """
        arg = to_message(clouddrive.pb2.UpdateMountPointRequest, arg)
        if async_:
            return self.async_stub.UpdateMountPoint(arg, metadata=self.metadata)
        else:
            return self.stub.UpdateMountPoint(arg, metadata=self.metadata)

    @overload
    def UpdatePromotionResult(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def UpdatePromotionResult(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def UpdatePromotionResult(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc UpdatePromotionResult(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.UpdatePromotionResult(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.UpdatePromotionResult(Empty(), metadata=self.metadata)
            return None

    @overload
    def UpdatePromotionResultByCloud(
        self, 
        arg: dict | clouddrive.pb2.UpdatePromotionResultByCloudRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def UpdatePromotionResultByCloud(
        self, 
        arg: dict | clouddrive.pb2.UpdatePromotionResultByCloudRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def UpdatePromotionResultByCloud(
        self, 
        arg: dict | clouddrive.pb2.UpdatePromotionResultByCloudRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc UpdatePromotionResultByCloud(UpdatePromotionResultByCloudRequest) returns (google.protobuf.Empty);

        ------------------- protobuf type definition -------------------

        message UpdatePromotionResultByCloudRequest {
          string cloudName = 1;
          string cloudAccountId = 2;
          string promotionId = 3;
        }
        """
        if async_:
            async def request():
                await self.async_stub.UpdatePromotionResultByCloud(arg, metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.UpdatePromotionResultByCloud(arg, metadata=self.metadata)
            return None

    @overload
    def UpdateSystem(
        self, 
        /, 
        async_: Literal[False] = False, 
    ) -> None:
        ...
    @overload
    def UpdateSystem(
        self, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, None]:
        ...
    def UpdateSystem(
        self, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> None | Coroutine[Any, Any, None]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc UpdateSystem(google.protobuf.Empty) returns (google.protobuf.Empty);
        """
        if async_:
            async def request():
                await self.async_stub.UpdateSystem(Empty(), metadata=self.metadata)
                return None
            return request()
        else:
            self.stub.UpdateSystem(Empty(), metadata=self.metadata)
            return None

    @overload
    def WalkThroughFolderTest(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.WalkThroughFolderResult:
        ...
    @overload
    def WalkThroughFolderTest(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.WalkThroughFolderResult]:
        ...
    def WalkThroughFolderTest(
        self, 
        arg: dict | clouddrive.pb2.FileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.WalkThroughFolderResult | Coroutine[Any, Any, clouddrive.pb2.WalkThroughFolderResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc WalkThroughFolderTest(FileRequest) returns (WalkThroughFolderResult);

        ------------------- protobuf type definition -------------------

        message FileRequest {
          string path = 1;
          bool forceRefresh = 2;
        }
        message WalkThroughFolderResult {
          uint64 totalFolderCount = 1;
          uint64 totalFileCount = 2;
          uint64 totalSize = 3;
        }
        """
        arg = to_message(clouddrive.pb2.FileRequest, arg)
        if async_:
            return self.async_stub.WalkThroughFolderTest(arg, metadata=self.metadata)
        else:
            return self.stub.WalkThroughFolderTest(arg, metadata=self.metadata)

    @overload
    def WriteToFile(
        self, 
        arg: dict | clouddrive.pb2.WriteFileRequest, 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.WriteFileResult:
        ...
    @overload
    def WriteToFile(
        self, 
        arg: dict | clouddrive.pb2.WriteFileRequest, 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.WriteFileResult]:
        ...
    def WriteToFile(
        self, 
        arg: dict | clouddrive.pb2.WriteFileRequest, 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.WriteFileResult | Coroutine[Any, Any, clouddrive.pb2.WriteFileResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc WriteToFile(WriteFileRequest) returns (WriteFileResult);

        ------------------- protobuf type definition -------------------

        message WriteFileRequest {
          uint64 fileHandle = 1;
          uint64 startPos = 2;
          uint64 length = 3;
          bytes buffer = 4;
          bool closeFile = 5;
        }
        message WriteFileResult {
          uint64 bytesWritten = 1;
        }
        """
        arg = to_message(clouddrive.pb2.WriteFileRequest, arg)
        if async_:
            return self.async_stub.WriteToFile(arg, metadata=self.metadata)
        else:
            return self.stub.WriteToFile(arg, metadata=self.metadata)

    @overload
    def WriteToFileStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.WriteFileRequest], 
        /, 
        async_: Literal[False] = False, 
    ) -> clouddrive.pb2.WriteFileResult:
        ...
    @overload
    def WriteToFileStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.WriteFileRequest], 
        /, 
        async_: Literal[True], 
    ) -> Coroutine[Any, Any, clouddrive.pb2.WriteFileResult]:
        ...
    def WriteToFileStream(
        self, 
        arg: Sequence[dict | clouddrive.pb2.WriteFileRequest], 
        /, 
        async_: Literal[False, True] = False, 
    ) -> clouddrive.pb2.WriteFileResult | Coroutine[Any, Any, clouddrive.pb2.WriteFileResult]:
        """

        ------------------- protobuf rpc definition --------------------

        rpc WriteToFileStream(stream WriteFileRequest) returns (WriteFileResult);

        ------------------- protobuf type definition -------------------

        message WriteFileRequest {
          uint64 fileHandle = 1;
          uint64 startPos = 2;
          uint64 length = 3;
          bytes buffer = 4;
          bool closeFile = 5;
        }
        message WriteFileResult {
          uint64 bytesWritten = 1;
        }
        """
        arg = [to_message(clouddrive.pb2.WriteFileRequest, a) for a in arg]
        if async_:
            return self.async_stub.WriteToFileStream(arg, metadata=self.metadata)
        else:
            return self.stub.WriteToFileStream(arg, metadata=self.metadata)

