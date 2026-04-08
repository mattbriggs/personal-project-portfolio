"""Unit tests for PlanService rendering pipeline."""

import pytest

from portfolio_manager.services.plan_service import PlanService


class _FakeProjectRepo:
    """Minimal fake repository for plan service tests."""

    def __init__(self, plan_content=""):
        from portfolio_manager.models.project import Project
        self._project = Project(id=1, name="Test", slug="test", plan_content=plan_content)
        self.saved_content: str | None = None

    def get(self, project_id):
        return self._project

    def update_plan(self, project_id, content):
        self.saved_content = content
        self._project.plan_content = content


@pytest.fixture
def plan_svc():
    return PlanService(_FakeProjectRepo(plan_content="# Hello\n\nWorld"))


class TestPlanService:
    def test_get_plan_returns_content(self, plan_svc):
        content = plan_svc.get_plan(1)
        assert content == "# Hello\n\nWorld"

    def test_save_plan_calls_repo(self, plan_svc):
        plan_svc.save_plan(1, "# New content")
        assert plan_svc._projects.saved_content == "# New content"

    def test_render_html_produces_full_document(self, plan_svc):
        html = plan_svc.render_html("# Title\n\nParagraph.")
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_render_html_includes_mermaid_script(self, plan_svc):
        html = plan_svc.render_html("# Test")
        assert "mermaid" in html.lower()

    def test_render_html_converts_heading(self, plan_svc):
        html = plan_svc.render_html("# My Heading")
        assert "<h1" in html
        assert "My Heading" in html

    def test_render_html_converts_paragraph(self, plan_svc):
        html = plan_svc.render_html("Hello world.")
        assert "<p>" in html
        assert "Hello world." in html

    def test_render_html_empty_input(self, plan_svc):
        html = plan_svc.render_html("")
        assert "<!DOCTYPE html>" in html  # still returns a valid shell
