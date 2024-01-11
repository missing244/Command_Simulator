SUBSCRIBE_EVENT = [
    "AdditionalContentLoaded","AgentCommand","AgentCreated","ApiInit","AppPaused","AppResumed","AppSuspended","AwardAchievement",
    "BlockBroken","BlockPlaced","BoardTextUpdated","BossKilled","CameraUsed","CauldronUsed","ChunkChanged","ChunkLoaded",
    "ChunkUnloaded","ConfigurationChanged","ConnectionFailed","CraftingSessionCompleted","EndOfDay","EntitySpawned",
    "FileTransmissionCancelled","FileTransmissionCompleted","FileTransmissionStarted","FirstTimeClientOpen","FocusGained",
    "FocusLost","GameSessionComplete","GameSessionStart","HardwareInfo","HasNewContent","ItemAcquired","ItemCrafted","ItemDestroyed",
    "ItemDropped","ItemEnchanted","ItemSmelted","ItemUsed","JoinCanceled","JukeboxUsed","LicenseCensus","MascotCreated","MenuShown",
    "MobInteracted","MobKilled","MultiplayerConnectionStateChanged","MultiplayerRoundEnd","MultiplayerRoundStart",
    "NpcPropertiesUpdated","OptionsUpdated","performanceMetrics","PackImportStage","PlayerBounced","PlayerDied","PlayerJoin",
    "PlayerLeave","PlayerMessage","PlayerTeleported","PlayerTransform","PlayerTravelled","PortalBuilt","PortalUsed","PortfolioExported",
    "PotionBrewed","PurchaseAttempt","PurchaseResolved","RegionalPopup","RespondedToAcceptContent","ScreenChanged","ScreenHeartbeat",
    "SignInToEdu","SignInToXboxLive","SignOutOfXboxLive","SpecialMobBuilt","StartClient","StartWorld","TextToSpeechToggled",
    "UgcDownloadCompleted","UgcDownloadStarted","UploadSkin","VehicleExited","WorldExported","WorldFilesListed","WorldGenerated",
    "WorldLoaded","WorldUnloaded"]

WEBSOCKET_HAND_SHAKE = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nconnection: Upgrade\r\nSec-WebSocket-Accept: %s\r\nWebSocket-Protocol: chat\r\n\r\n"
HASH_SALT = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

MAX_COMMAND_QUEUE = 100

SUBSCRIBE_EVENT_JSON = {
    "body": {"eventName": ""},
    "header": {
        "requestId": "",
        "messagePurpose": "subscribe",
        "version": 1,
        "messageType": "commandRequest"
    }
}

UNSUBSCRIBE_EVENT_JSON = {
    "body": {"eventName": ""},
    "header": {
        "requestId": "",
        "messagePurpose": "unsubscribe",
        "version": 1,
        "messageType": "commandRequest"
    }
}

RUN_COMMAND_JSON = {
    "body": {
        "origin": {"type": "player"},
        "commandLine": "",
        "version": 1
    },
    "header": {
        "requestId": "",
        "messagePurpose": "commandRequest",
        "version": 1,
        "messageType": "commandRequest"
    }
}
