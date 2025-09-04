import pytest
import json
import base64
import sys
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from opentelemetry import trace

sys.modules["openlit"] = MagicMock()

from agentuity.server.response import AgentResponse  # noqa: E402
from agentuity.server.agent import RemoteAgent, Data  # noqa: E402
from agentuity.server.context import AgentContext  # noqa: E402


class TestAgentResponseExtended:
    """Extended test suite for the AgentResponse class."""

    @pytest.fixture
    def mock_tracer(self):
        """Create a mock tracer for testing."""
        return MagicMock(spec=trace.Tracer)

    @pytest.fixture
    def mock_agents_by_id(self):
        """Create a mock agents_by_id dict for testing."""
        return {
            "agent_123": {
                "id": "agent_123",
                "name": "test_agent",
                "run": MagicMock(),
            },
            "agent_456": {
                "id": "agent_456",
                "name": "another_agent",
                "run": MagicMock(),
            },
        }

    @pytest.fixture
    def mock_context(self, mock_tracer, mock_agents_by_id):
        """Create a mock AgentContext for testing."""
        context = MagicMock(spec=AgentContext)
        context.tracer = mock_tracer
        context.agents_by_id = mock_agents_by_id
        context.port = 3500
        context.base_url = "https://api.example.com"
        context.api_key = "test_api_key"
        return context

    @pytest.fixture
    def agent_response(self, mock_context):
        """Create an AgentResponse instance for testing."""
        reader = asyncio.StreamReader()
        reader.feed_data(b"Hello, world!")
        reader.feed_eof()

        data = Data("text/plain", reader)
        return AgentResponse(mock_context, data)

    def test_handoff_with_id(self, agent_response, mock_tracer, mock_agents_by_id):
        """Test handoff to another agent using ID."""
        # Test that handoff sets up deferred execution parameters
        result = agent_response.handoff({"id": "agent_456"})

        assert result == agent_response  # Should return self for chaining
        assert agent_response.has_pending_handoff is True
        assert agent_response._handoff_params["params"]["id"] == "agent_456"
        assert agent_response._handoff_params["args"] is None
        assert agent_response._handoff_params["metadata"] is None

    def test_handoff_with_name(self, agent_response, mock_tracer, mock_agents_by_id):
        """Test handoff to another agent using name."""
        # Test that handoff sets up deferred execution parameters
        result = agent_response.handoff({"name": "another_agent"})

        assert result == agent_response  # Should return self for chaining
        assert agent_response.has_pending_handoff is True
        assert agent_response._handoff_params["params"]["name"] == "another_agent"
        assert agent_response._handoff_params["args"] is None
        assert agent_response._handoff_params["metadata"] is None

    def test_handoff_with_args(self, agent_response, mock_tracer, mock_agents_by_id):
        """Test handoff with custom arguments."""
        args = {"message": "Custom message"}
        metadata = {"custom_key": "custom_value"}
        result = agent_response.handoff({"id": "agent_456"}, args, metadata)

        assert result == agent_response  # Should return self for chaining
        assert agent_response.has_pending_handoff is True
        assert agent_response._handoff_params["params"]["id"] == "agent_456"
        assert agent_response._handoff_params["args"] == args
        assert agent_response._handoff_params["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_execute_handoff_with_id(
        self, agent_response, mock_tracer, mock_agents_by_id
    ):
        """Test actual execution of handoff to another agent using ID."""
        mock_remote_agent = AsyncMock(spec=RemoteAgent)
        mock_response_data = MagicMock()
        mock_response_data.data.content_type = "application/json"
        mock_response_data.data.base64 = base64.b64encode(
            json.dumps({"result": "success"}).encode()
        ).decode()
        mock_response_data.metadata = {"response_key": "response_value"}

        # Mock the data.stream() method
        async def mock_stream():
            reader = asyncio.StreamReader()
            reader.feed_data(b'{"result": "success"}')
            reader.feed_eof()
            return reader

        mock_response_data.data.stream = mock_stream
        mock_remote_agent.run.return_value = mock_response_data

        with (
            patch(
                "agentuity.server.response.resolve_agent",
                return_value=mock_remote_agent,
            ),
        ):
            # First, set up the handoff
            agent_response.handoff({"id": "agent_456"})
            assert agent_response.has_pending_handoff is True

            # Then execute it
            result = await agent_response._execute_handoff()

            assert result == agent_response
            assert agent_response.has_pending_handoff is False
            assert agent_response._metadata == {"response_key": "response_value"}
            assert agent_response.content_type == "application/json"
            mock_remote_agent.run.assert_called_once()

    def test_handoff_missing_id_and_name(self, agent_response):
        """Test handoff with missing ID and name."""
        with pytest.raises(ValueError, match="params must have an id or name"):
            agent_response.handoff({})

    @pytest.mark.asyncio
    async def test_execute_handoff_agent_not_found(self, agent_response):
        """Test handoff execution when agent is not found."""
        with patch("agentuity.server.response.resolve_agent", return_value=None):
            agent_response.handoff({"id": "nonexistent_agent"})

            with pytest.raises(
                ValueError,
                match="Handoff failed: Agent 'nonexistent_agent' could not be resolved",
            ):
                await agent_response._execute_handoff()

    @pytest.mark.asyncio
    async def test_execute_handoff_resolve_error(self, agent_response):
        """Test handoff execution when resolve_agent raises error."""
        with patch(
            "agentuity.server.response.resolve_agent",
            side_effect=ValueError("access denied"),
        ):
            agent_response.handoff({"id": "restricted_agent"})

            with pytest.raises(
                ValueError,
                match="Handoff failed: Agent 'restricted_agent' not found or not accessible",
            ):
                await agent_response._execute_handoff()

    @pytest.mark.asyncio
    async def test_execute_handoff_agent_execution_failure(self, agent_response):
        """Test handoff execution when target agent fails."""
        mock_agent = AsyncMock()
        mock_agent.run.side_effect = Exception("Agent crashed")

        with patch("agentuity.server.response.resolve_agent", return_value=mock_agent):
            agent_response.handoff({"id": "failing_agent"})

            with pytest.raises(
                Exception,
                match="Handoff execution failed for agent 'failing_agent': Agent crashed",
            ):
                await agent_response._execute_handoff()

    def test_html(self, agent_response):
        """Test setting an HTML response."""
        html_content = "<html><body>Hello, world!</body></html>"
        metadata = {"key": "value"}

        result = agent_response.html(html_content, metadata)

        assert result == agent_response  # Should return self for chaining
        assert agent_response.content_type == "text/html"
        assert agent_response._metadata == metadata

        assert isinstance(agent_response._payload, str)
        assert agent_response._payload == html_content

    def test_pdf(self, agent_response):
        """Test setting a PDF response."""
        pdf_data = b"%PDF-1.5 test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.pdf(pdf_data, metadata)

            mock_binary.assert_called_once_with(pdf_data, "application/pdf", metadata)
            assert result == agent_response

    def test_png(self, agent_response):
        """Test setting a PNG response."""
        png_data = b"PNG test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.png(png_data, metadata)

            mock_binary.assert_called_once_with(png_data, "image/png", metadata)
            assert result == agent_response

    def test_jpeg(self, agent_response):
        """Test setting a JPEG response."""
        jpeg_data = b"JPEG test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.jpeg(jpeg_data, metadata)

            mock_binary.assert_called_once_with(jpeg_data, "image/jpeg", metadata)
            assert result == agent_response

    def test_gif(self, agent_response):
        """Test setting a GIF response."""
        gif_data = b"GIF test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.gif(gif_data, metadata)

            mock_binary.assert_called_once_with(gif_data, "image/gif", metadata)
            assert result == agent_response

    def test_webp(self, agent_response):
        """Test setting a WebP response."""
        webp_data = b"WebP test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.webp(webp_data, metadata)

            mock_binary.assert_called_once_with(webp_data, "image/webp", metadata)
            assert result == agent_response

    def test_webm(self, agent_response):
        """Test setting a WebM response."""
        webm_data = b"WebM test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.webm(webm_data, metadata)

            mock_binary.assert_called_once_with(webm_data, "video/webm", metadata)
            assert result == agent_response

    def test_mp3(self, agent_response):
        """Test setting an MP3 response."""
        mp3_data = b"MP3 test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.mp3(mp3_data, metadata)

            mock_binary.assert_called_once_with(mp3_data, "audio/mpeg", metadata)
            assert result == agent_response

    def test_mp4(self, agent_response):
        """Test setting an MP4 response."""
        mp4_data = b"MP4 test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.mp4(mp4_data, metadata)

            mock_binary.assert_called_once_with(mp4_data, "video/mp4", metadata)
            assert result == agent_response

    def test_m4a(self, agent_response):
        """Test setting an M4A response."""
        m4a_data = b"M4A test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.m4a(m4a_data, metadata)

            mock_binary.assert_called_once_with(m4a_data, "audio/m4a", metadata)
            assert result == agent_response

    def test_wav(self, agent_response):
        """Test setting a WAV response."""
        wav_data = b"WAV test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.wav(wav_data, metadata)

            mock_binary.assert_called_once_with(wav_data, "audio/wav", metadata)
            assert result == agent_response

    def test_ogg(self, agent_response):
        """Test setting an OGG response."""
        ogg_data = b"OGG test data"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.ogg(ogg_data, metadata)

            mock_binary.assert_called_once_with(ogg_data, "audio/ogg", metadata)
            assert result == agent_response

    def test_data_with_bytes(self, agent_response):
        """Test setting data with bytes."""
        binary_data = b"Binary test data"
        content_type = "application/custom"
        metadata = {"key": "value"}

        with patch("agentuity.server.response.AgentResponse.binary") as mock_binary:
            mock_binary.return_value = agent_response
            result = agent_response.data(binary_data, content_type, metadata)

            mock_binary.assert_called_once_with(binary_data, content_type, metadata)
            assert result == agent_response

    def test_data_with_string(self, agent_response):
        """Test setting data with string."""
        string_data = "String test data"
        content_type = "text/custom"
        metadata = {"key": "value"}

        result = agent_response.data(string_data, content_type, metadata)

        assert result == agent_response
        assert agent_response.content_type == content_type
        assert agent_response._metadata == metadata

        assert agent_response._payload == string_data

    def test_data_with_dict(self, agent_response):
        """Test setting data with dictionary."""
        dict_data = {"message": "Test data"}
        content_type = "application/custom+json"
        metadata = {"key": "value"}

        result = agent_response.data(dict_data, content_type, metadata)

        assert result == agent_response
        assert agent_response.content_type == content_type
        assert agent_response._metadata == metadata

        assert agent_response._payload == json.dumps(dict_data)

    def test_data_with_other_type(self, agent_response):
        """Test setting data with other type."""
        other_data = 12345
        content_type = "text/custom"
        metadata = {"key": "value"}

        result = agent_response.data(other_data, content_type, metadata)

        assert result == agent_response
        assert agent_response.content_type == content_type
        assert agent_response._metadata == metadata

        assert agent_response._payload == str(other_data)

    def test_markdown(self, agent_response):
        """Test setting a markdown response."""
        markdown_content = "# Hello\n\nThis is **markdown**."
        metadata = {"key": "value"}

        result = agent_response.markdown(markdown_content, metadata)

        assert result == agent_response
        assert agent_response.content_type == "text/markdown"
        assert agent_response._metadata == metadata

        assert agent_response._payload == markdown_content
