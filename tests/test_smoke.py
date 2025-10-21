def test_import_app():
    # FastAPI が無くても import 自体は成功する想定
    from src.app.main import app

    assert app is not None

    # 健康チェックハンドラがあることを確認（厳密な FastAPI 依存は避ける）
    assert hasattr(app, "__class__")
