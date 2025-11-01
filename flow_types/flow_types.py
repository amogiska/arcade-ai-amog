"""Type definitions for Arcade flow.json data structures."""

from typing import Any, Literal, NotRequired, TypedDict


class Timestamp(TypedDict):
    """Firestore timestamp structure."""

    _seconds: int
    _nanoseconds: int


class AutoplayConfig(TypedDict):
    """Autoplay configuration."""

    enabled: bool
    delay: int | None


class SharePageLayout(TypedDict):
    """Share page layout configuration."""

    type: str
    showHeader: bool
    showLogo: bool
    showButton: bool


class ClickEvent(TypedDict):
    """Click event captured during flow."""

    type: Literal["click"]
    clickId: str
    frameX: float
    frameY: float
    timeMs: int
    tabId: int
    frameId: int


class TypingEvent(TypedDict):
    """Typing event captured during flow."""

    type: Literal["typing"]
    startTimeMs: int
    endTimeMs: int
    tabId: int
    frameId: int


class ScrollingEvent(TypedDict):
    """Scrolling event captured during flow."""

    type: Literal["scrolling"]
    startTimeMs: int
    endTimeMs: int
    tabId: int
    frameId: int


class DraggingEvent(TypedDict):
    """Dragging event captured during flow."""

    type: Literal["dragging"]
    startTimeMs: int
    endTimeMs: int
    tabId: int
    frameId: int


# Union type for all captured events
CapturedEvent = ClickEvent | TypingEvent | ScrollingEvent | DraggingEvent


class AIContext(TypedDict):
    """AI processing context."""

    recordingEndRequestId: str
    recordingEndVersionId: str


class Size(TypedDict):
    """Image/video size dimensions."""

    width: int
    height: int


class Hotspot(TypedDict):
    """Interactive hotspot on an image step."""

    id: str
    width: int
    height: int
    label: str
    style: str
    defaultOpen: bool
    textColor: str
    bgColor: str
    x: float
    y: float


class PageContext(TypedDict):
    """Page context information."""

    url: str
    title: str
    description: str
    width: int
    height: int
    language: str


class OriginalRect(TypedDict):
    """Original rectangle dimensions for click context."""

    x: int
    y: int
    width: int
    height: int


class ClickContext(TypedDict):
    """Context information about a clicked element."""

    cssSelector: str
    text: str
    elementType: str
    sections: list[str]
    originalRect: OriginalRect


class PanAndZoom(TypedDict):
    """Pan and zoom configuration."""

    enabled: bool


class PathConfig(TypedDict):
    """Path configuration for chapter steps."""

    id: str
    buttonText: str
    buttonColor: str
    buttonTextColor: str
    pathType: str
    url: NotRequired[str]


class ChapterStep(TypedDict):
    """Chapter step in the flow."""

    type: Literal["CHAPTER"]
    id: str
    title: str
    subtitle: str
    theme: NotRequired[str]
    textAlign: NotRequired[str]
    showPreviewImage: NotRequired[bool]
    showLogo: NotRequired[bool]
    paths: list[PathConfig]


class ImageStep(TypedDict):
    """Image step in the flow."""

    id: str
    type: Literal["IMAGE"]
    url: str
    originalImageUrl: str
    blurhash: str
    hasHTML: bool
    size: Size
    hotspots: list[Hotspot]
    pageContext: PageContext
    clickContext: NotRequired[ClickContext]
    assetId: str
    panAndZoom: NotRequired[PanAndZoom]


class VideoStep(TypedDict):
    """Video step in the flow."""

    id: str
    type: Literal["VIDEO"]
    url: str
    startTimeFrac: float
    endTimeFrac: float
    playbackRate: float
    duration: float
    videoProcessing: bool
    muted: bool
    videoThumbnailUrl: str
    size: Size
    assetId: str


# Union type for all step types
Step = ChapterStep | ImageStep | VideoStep


class CustomVariable(TypedDict):
    """Custom variable definition."""

    fallback: str
    createdAt: Timestamp


class FlowData(TypedDict):
    """Complete Arcade flow.json data structure."""

    createdBy: str
    externalName: str | None
    description: str
    schemaVersion: str
    cta: dict[str, Any]
    editors: list[Any]
    optimizeFlowForMobileView: bool
    folderId: str | None
    themeId: str | None
    menu: Any | None
    showCaptions: bool
    teamId: str
    showFlowNavIndicator: str
    flowWrapper: int
    customCursor: int
    font: str
    showStartOverlay: bool
    showBackNextButtons: bool
    startOverlayButtonText: str
    autoplay: AutoplayConfig
    backgroundMusicUrl: str | None
    backgroundMusicVolume: float
    sharePageLayout: SharePageLayout
    useVersioning: bool
    createdWith: str
    uploadId: str
    hasUsedAI: bool
    created: Timestamp
    capturedEvents: list[CapturedEvent]
    ai: AIContext
    aspectRatio: float
    status: int
    processedAIReason: str
    useCase: str
    name: str
    steps: list[Step]
    processedAI: bool
    lastModifiedBy: str
    modified: Timestamp
    customVariables: dict[str, CustomVariable]
