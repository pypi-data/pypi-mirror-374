from pathlib import Path
from typing import TYPE_CHECKING

from httpx import AsyncClient
from UnityPy.enums.ClassIDType import ClassIDType

from albi0.extract.extractor import Extractor
from albi0.extract.registry import AssetPostHandlerGroup, ObjPreHandlerGroup
from albi0.typing import ObjectPath
from albi0.update import Downloader, Updater
from albi0.updaters import YooVersionManager

if TYPE_CHECKING:
	from UnityPy.classes import Texture2D


header = {
	'user-agent': r'Mozilla/5.0 (Linux; Android 6.0.1; RIDGE 4G Build/LRX22G)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2887.55 Mobile Safari/537.36',
	'referer': r'https://newseer.61.com',
}

downloader = Downloader(AsyncClient())

obj_pre = ObjPreHandlerGroup()
asset_post = AssetPostHandlerGroup()
Extractor(
	'newseer',
	'赛尔号资源提取器',
	asset_posthandler_group=asset_post,
	obj_prehandler_group=obj_pre,
)


@obj_pre.register(ClassIDType.Sprite)
@obj_pre.register(ClassIDType.Texture2D)
def texture2d_prehandler(
	obj: 'Texture2D', obj_path: ObjectPath
) -> tuple['Texture2D', ObjectPath]:
	if obj.image.mode == 'RGBA' and obj_path.suffix != '.png':
		obj_path = obj_path.with_suffix('.png')
	return obj, obj_path


Updater(
	'newseer.default',
	'赛尔号AB包下载器 DefaultPackage部分',
	version_manager=YooVersionManager(
		'DefaultPackage',
		remote_path='https://newseer.61.com/Assets/StandaloneWindows64/DefaultPackage/',
		local_path=Path('./newseer/assetbundles/DefaultPackage/'),
		version_factory=int,
	),
	downloader=downloader,
)


Updater(
	'newseer.pet',
	'赛尔号AB包下载器 PetAnimPackage部分',
	version_manager=YooVersionManager(
		'PetAnimPackage',
		remote_path='https://newseer.61.com/Assets/StandaloneWindows64/PetAnimPackage/',
		local_path=Path('./newseer/assetbundles/PetAnimPackage/'),
		version_factory=int,
	),
	downloader=downloader,
)

Updater(
	'newseer.startup',
	'赛尔号AB包下载器 StartupPackage部分',
	version_manager=YooVersionManager(
		'StartupPackage',
		remote_path='https://newseer.61.com/Assets/StandaloneWindows64/StartupPackage/',
		local_path=Path('./newseer/assetbundles/StartupPackage/'),
		version_factory=int,
	),
	downloader=downloader,
)
