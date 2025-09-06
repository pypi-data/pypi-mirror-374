"""VoiceVox API client library with modular design and comprehensive type support."""

import requests
import json
import os
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass
from abc import ABC, abstractmethod
from tqdm import tqdm


class TextToSpeechRequest(TypedDict):
    """Type definition for concurrent text-to-speech request parameters.
    
    Required fields:
        text: Text to synthesize
        speaker_id: Speaker ID
        
    Optional fields:
        enable_katakana_english: Enable katakana pronunciation for English (default: True)
        enable_interrogative_upspeak: Enable interrogative upspeak (default: True)
        core_version: Specific core version (default: None)
        speed_scale: Speech speed multiplier (default: 1.0)
        pitch_scale: Pitch adjustment multiplier (default: 0)
        intonation_scale: Intonation strength multiplier (default: 1.0)
        volume_scale: Volume multiplier (default: 1.0)
        pre_phoneme_length: Silence duration before speech in seconds (default: 0.1)
        post_phoneme_length: Silence duration after speech in seconds (default: 0.1)
        pause_length: Pause length between phrases in seconds (default: None)
        pause_length_scale: Pause length multiplier (default: 1.0)
    """
    text: str
    speaker_id: int
    # Optional fields
    enable_katakana_english: Optional[bool]
    enable_interrogative_upspeak: Optional[bool]
    core_version: Optional[str]
    speed_scale: Optional[float]
    pitch_scale: Optional[float]
    intonation_scale: Optional[float]
    volume_scale: Optional[float]
    pre_phoneme_length: Optional[float]
    post_phoneme_length: Optional[float]
    pause_length: Optional[float]
    pause_length_scale: Optional[float]


@dataclass
class AudioQuery:
    """Audio synthesis query parameters.
    
    Args:
        accent_phrases: List of accent phrase dictionaries
        speedScale: Speech speed multiplier (1.0 = normal)
        pitchScale: Pitch adjustment multiplier (1.0 = normal)
        intonationScale: Intonation strength multiplier (1.0 = normal)
        volumeScale: Volume multiplier (1.0 = normal)
        prePhonemeLength: Silence duration before speech (seconds)
        postPhonemeLength: Silence duration after speech (seconds)
        outputSamplingRate: Audio sampling rate (Hz)
        outputStereo: Whether to output stereo audio
        kana: Optional kana representation of text
        pauseLength: Optional pause length (seconds)
        pauseLengthScale: Pause length multiplier (1.0 = normal)
    """
    accent_phrases: List[Dict]
    speedScale: float
    pitchScale: float
    intonationScale: float
    volumeScale: float
    prePhonemeLength: float
    postPhonemeLength: float
    outputSamplingRate: int
    outputStereo: bool
    kana: Optional[str] = None
    pauseLength: Optional[float] = None
    pauseLengthScale: float = 1.0


@dataclass
class Speaker:
    """VoiceVox speaker information.
    
    Args:
        name: Speaker display name
        speaker_uuid: Unique speaker identifier
        styles: List of available voice styles
        version: Speaker model version
        supported_features: Optional feature support information
    """
    name: str
    speaker_uuid: str
    styles: List[Dict]
    version: str
    supported_features: Optional[Dict] = None


@dataclass
class Preset:
    """Voice synthesis preset configuration.
    
    Args:
        id: Preset identifier
        name: Preset display name
        speaker_uuid: Associated speaker UUID
        style_id: Speaker style ID
        speedScale: Speech speed multiplier
        pitchScale: Pitch adjustment multiplier
        intonationScale: Intonation strength multiplier
        volumeScale: Volume multiplier
        prePhonemeLength: Pre-speech silence duration
        postPhonemeLength: Post-speech silence duration
        pauseLength: Pause duration between phrases
        pauseLengthScale: Pause length multiplier
    """
    id: int
    name: str
    speaker_uuid: str
    style_id: int
    speedScale: float
    pitchScale: float
    intonationScale: float
    volumeScale: float
    prePhonemeLength: float
    postPhonemeLength: float
    pauseLength: float = 0.1
    pauseLengthScale: float = 1.0


class VoiceVoxError(Exception):
    """Exception raised for VoiceVox API errors."""
    pass


class QuerySerializer:
    """Utility class for serializing AudioQuery objects to API format."""
    
    @staticmethod
    def serialize_audio_query(audio_query: AudioQuery) -> Dict[str, Any]:
        """Convert AudioQuery to API-compatible dictionary.
        
        Args:
            audio_query: AudioQuery object to serialize
            
        Returns:
            Dictionary representation for API requests
        """
        query_dict = {
            'accent_phrases': audio_query.accent_phrases,
            'speedScale': audio_query.speedScale,
            'pitchScale': audio_query.pitchScale,
            'intonationScale': audio_query.intonationScale,
            'volumeScale': audio_query.volumeScale,
            'prePhonemeLength': audio_query.prePhonemeLength,
            'postPhonemeLength': audio_query.postPhonemeLength,
            'outputSamplingRate': audio_query.outputSamplingRate,
            'outputStereo': audio_query.outputStereo
        }
        
        if audio_query.kana:
            query_dict['kana'] = audio_query.kana
        if audio_query.pauseLength is not None:
            query_dict['pauseLength'] = audio_query.pauseLength
        if audio_query.pauseLengthScale != 1.0:
            query_dict['pauseLengthScale'] = audio_query.pauseLengthScale
            
        return query_dict
    
    @staticmethod
    def serialize_preset(preset: Preset) -> Dict[str, Any]:
        """Convert Preset to API-compatible dictionary.
        
        Args:
            preset: Preset object to serialize
            
        Returns:
            Dictionary representation for API requests
        """
        return {
            'id': preset.id,
            'name': preset.name,
            'speaker_uuid': preset.speaker_uuid,
            'style_id': preset.style_id,
            'speedScale': preset.speedScale,
            'pitchScale': preset.pitchScale,
            'intonationScale': preset.intonationScale,
            'volumeScale': preset.volumeScale,
            'prePhonemeLength': preset.prePhonemeLength,
            'postPhonemeLength': preset.postPhonemeLength,
            'pauseLength': preset.pauseLength,
            'pauseLengthScale': preset.pauseLengthScale
        }


class BaseHTTPClient(ABC):
    """Abstract base class for HTTP client implementations."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize base HTTP client.
        
        Args:
            api_key: VoiceVox API key (defaults to VOICEVOX_API_KEY env var)
            base_url: API base URL (defaults to VOICEVOX_URL env var)
        """
        self.api_key = api_key or os.getenv('VOICEVOX_API_KEY')
        self.base_url = (base_url or os.getenv('VOICEVOX_URL'))
        self.serializer = QuerySerializer()
    
    @abstractmethod
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None, return_binary: bool = False) -> Any:
        """Make HTTP request (abstract method)."""
        pass


class VoiceVoxSyncClient(BaseHTTPClient):
    """Synchronous VoiceVox API client."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize synchronous VoiceVox client.
        
        Args:
            api_key: VoiceVox API key (defaults to VOICEVOX_API_KEY env var)
            base_url: API base URL (defaults to VOICEVOX_URL env var)
        """
        super().__init__(api_key, base_url)
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None, return_binary: bool = False) -> Any:
        """Make synchronous HTTP request to VoiceVox API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            json_data: JSON request body
            return_binary: Whether to return binary content
            
        Returns:
            API response data or binary content
            
        Raises:
            VoiceVoxError: If API request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=600
            )
            
            if response.status_code >= 400:
                error_detail = self._extract_error_detail(response)
                raise VoiceVoxError(f"API Error {response.status_code}: {error_detail}")
            
            return response.content if return_binary else self._parse_response(response)
            
        except requests.RequestException as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")
    
    def _extract_error_detail(self, response: requests.Response) -> str:
        """Extract error details from response."""
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text
    
    def _parse_response(self, response: requests.Response) -> Optional[Any]:
        """Parse non-binary response content."""
        return response.json() if response.content else None
    
    def get_speakers(self, core_version: Optional[str] = None) -> List[Speaker]:
        """Get list of available speakers.
        
        Args:
            core_version: Optional specific core version to query
            
        Returns:
            List of available speakers
        """
        params = {'core_version': core_version} if core_version else {}
        response = self._make_request('GET', '/speakers', params=params)
        return [Speaker(**speaker) for speaker in response]
    
    def get_speaker_info(self, speaker_uuid: str, resource_format: str = "base64", 
                        core_version: Optional[str] = None) -> Dict:
        """Get detailed information about a specific speaker.
        
        Args:
            speaker_uuid: Speaker UUID
            resource_format: Resource format (base64, etc.)
            core_version: Optional specific core version
            
        Returns:
            Speaker information dictionary
        """
        params = {
            'speaker_uuid': speaker_uuid,
            'resource_format': resource_format
        }
        if core_version:
            params['core_version'] = core_version
            
        return self._make_request('GET', '/speaker_info', params=params)
    
    def get_singers(self, core_version: Optional[str] = None) -> List[Speaker]:
        """Get list of available singers (singing voice models).
        
        Args:
            core_version: Optional specific core version to query
            
        Returns:
            List of available singers
        """
        params = {'core_version': core_version} if core_version else {}
        response = self._make_request('GET', '/singers', params=params)
        return [Speaker(**singer) for singer in response]
    
    def text_to_speech(self, text: str, speaker_id: int, 
                      enable_katakana_english: bool = True,
                      enable_interrogative_upspeak: bool = True,
                      core_version: Optional[str] = None,
                      speed_scale: float = 1.0,
                      pitch_scale: float = 0,
                      intonation_scale: float = 1.0,
                      volume_scale: float = 1.0,
                      pre_phoneme_length: float = 0.1,
                      post_phoneme_length: float = 0.1,
                      pause_length: Optional[float] = None,
                      pause_length_scale: float = 1.0) -> bytes:
        """Convert text directly to speech audio with customizable parameters.
        
        Args:
            text: Text to synthesize
            speaker_id: Speaker ID
            enable_katakana_english: Enable katakana pronunciation for English
            enable_interrogative_upspeak: Enable interrogative upspeak
            core_version: Optional specific core version
            speed_scale: Speech speed multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
            pitch_scale: Pitch adjustment multiplier (1.0 = normal)
            intonation_scale: Intonation strength multiplier (1.0 = normal)
            volume_scale: Volume multiplier (1.0 = normal)
            pre_phoneme_length: Silence duration before speech (seconds)
            post_phoneme_length: Silence duration after speech (seconds)
            pause_length: Optional pause length between phrases (seconds)
            pause_length_scale: Pause length multiplier (1.0 = normal)
            
        Returns:
            Audio data as bytes
        """
        # Create audio query directly via API
        query_params = {
            'text': text,
            'speaker': speaker_id,
            'enable_katakana_english': enable_katakana_english
        }
        if core_version:
            query_params['core_version'] = core_version
        
        response = self._make_request('POST', '/audio_query', params=query_params)
        audio_query = AudioQuery(**response)
        
        # Apply custom parameters
        audio_query.speedScale = speed_scale
        audio_query.pitchScale = pitch_scale
        audio_query.intonationScale = intonation_scale
        audio_query.volumeScale = volume_scale
        audio_query.prePhonemeLength = pre_phoneme_length
        audio_query.postPhonemeLength = post_phoneme_length
        if pause_length is not None:
            audio_query.pauseLength = pause_length
        audio_query.pauseLengthScale = pause_length_scale
        
        # Synthesize directly via API
        synth_params = {
            'speaker': speaker_id,
            'enable_interrogative_upspeak': enable_interrogative_upspeak
        }
        if core_version:
            synth_params['core_version'] = core_version
            
        query_dict = self.serializer.serialize_audio_query(audio_query)
        return self._make_request('POST', '/synthesis', params=synth_params, 
                                json_data=query_dict, return_binary=True)
    
    def multi_synthesis(self, queries: List[AudioQuery], speaker: int,
                       enable_interrogative_upspeak: bool = True,
                       core_version: Optional[str] = None) -> bytes:
        """Synthesize multiple audio queries into a single audio stream.
        
        Args:
            queries: List of AudioQuery objects to synthesize
            speaker: Speaker ID
            enable_interrogative_upspeak: Enable interrogative upspeak
            core_version: Optional specific core version
            
        Returns:
            Combined audio data as bytes
        """
        params = {
            'speaker': speaker,
            'enable_interrogative_upspeak': enable_interrogative_upspeak
        }
        if core_version:
            params['core_version'] = core_version
            
        query_dicts = [self.serializer.serialize_audio_query(query) for query in queries]
        return self._make_request('POST', '/multi_synthesis', params=params,
                                json_data=query_dicts, return_binary=True)
    
    def get_presets(self) -> List[Preset]:
        """Get list of available voice presets.
        
        Returns:
            List of available presets
        """
        response = self._make_request('GET', '/presets')
        return [Preset(**preset) for preset in response]
    
    def add_preset(self, preset: Preset) -> int:
        """Add a new voice preset.
        
        Args:
            preset: Preset object to add
            
        Returns:
            Preset ID of the added preset
        """
        preset_dict = self.serializer.serialize_preset(preset)
        return self._make_request('POST', '/add_preset', json_data=preset_dict)
    
    def update_preset(self, preset: Preset) -> int:
        """Update an existing voice preset.
        
        Args:
            preset: Preset object with updated values
            
        Returns:
            Preset ID of the updated preset
        """
        preset_dict = self.serializer.serialize_preset(preset)
        return self._make_request('POST', '/update_preset', json_data=preset_dict)
    
    def delete_preset(self, preset_id: int) -> None:
        """Delete a voice preset.
        
        Args:
            preset_id: ID of preset to delete
        """
        params = {'id': preset_id}
        self._make_request('POST', '/delete_preset', params=params)
    
    def get_version(self) -> str:
        """Get VoiceVox engine version.
        
        Returns:
            Version string
        """
        return self._make_request('GET', '/version')
    
    def get_core_versions(self) -> List[str]:
        """Get list of available core versions.
        
        Returns:
            List of core version strings
        """
        return self._make_request('GET', '/core_versions')
    
    def get_supported_devices(self, core_version: Optional[str] = None) -> Dict:
        """Get supported devices information.
        
        Args:
            core_version: Optional specific core version
            
        Returns:
            Supported devices information
        """
        params = {'core_version': core_version} if core_version else {}
        return self._make_request('GET', '/supported_devices', params=params)
    
    def get_engine_manifest(self) -> Dict:
        """Get engine manifest information.
        
        Returns:
            Engine manifest dictionary
        """
        return self._make_request('GET', '/engine_manifest')
    
    def initialize_speaker(self, speaker: int, skip_reinit: bool = False,
                          core_version: Optional[str] = None) -> None:
        """Initialize speaker model.
        
        Args:
            speaker: Speaker ID
            skip_reinit: Skip reinitialization if already initialized
            core_version: Optional specific core version
        """
        params = {
            'speaker': speaker,
            'skip_reinit': skip_reinit
        }
        if core_version:
            params['core_version'] = core_version
            
        self._make_request('POST', '/initialize_speaker', params=params)
    
    def is_initialized_speaker(self, speaker: int, core_version: Optional[str] = None) -> bool:
        """Check if speaker is initialized.
        
        Args:
            speaker: Speaker ID
            core_version: Optional specific core version
            
        Returns:
            True if speaker is initialized
        """
        params = {'speaker': speaker}
        if core_version:
            params['core_version'] = core_version
            
        return self._make_request('GET', '/is_initialized_speaker', params=params)
    
    def save_audio(self, audio_data: bytes, filename: str) -> None:
        """Save audio data to file.
        
        Args:
            audio_data: Audio data bytes
            filename: Output filename
        """
        with open(filename, 'wb') as f:
            f.write(audio_data)
    
    def connect_waves(self, wave_data_list: List[str]) -> bytes:
        """Connect multiple wave data into single audio stream.
        
        Args:
            wave_data_list: List of base64-encoded wave data
            
        Returns:
            Connected audio data as bytes
        """
        return self._make_request('POST', '/connect_waves', json_data=wave_data_list, 
                                return_binary=True)
    


class VoiceVoxAsyncClient(BaseHTTPClient):
    """Asynchronous VoiceVox API client."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize asynchronous VoiceVox client.
        
        Args:
            api_key: VoiceVox API key (defaults to VOICEVOX_API_KEY env var)
            base_url: API base URL (defaults to VOICEVOX_URL env var)
        """
        super().__init__(api_key, base_url)
        self._async_session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Enter async context manager."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        timeout = aiohttp.ClientTimeout(total=600)
        self._async_session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        if self._async_session:
            await self._async_session.close()
            self._async_session = None
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None, return_binary: bool = False) -> Any:
        """Sync interface not available for async client."""
        raise NotImplementedError("Use async methods for async client")
    
    async def _make_async_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                                 json_data: Optional[Dict] = None, return_binary: bool = False) -> Any:
        """Make asynchronous HTTP request to VoiceVox API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            json_data: JSON request body
            return_binary: Whether to return binary content
            
        Returns:
            API response data or binary content
            
        Raises:
            VoiceVoxError: If API request fails
        """
        if not self._async_session:
            raise VoiceVoxError("Async session not initialized. Use 'async with VoiceVoxAsyncClient()' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self._async_session.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            ) as response:
                
                if response.status >= 400:
                    error_detail = await self._extract_error_detail_async(response)
                    raise VoiceVoxError(f"API Error {response.status}: {error_detail}")
                
                return await response.read() if return_binary else await self._parse_response_async(response)
                    
        except aiohttp.ClientError as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")
    
    async def _extract_error_detail_async(self, response: aiohttp.ClientResponse) -> str:
        """Extract error details from async response."""
        try:
            return await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError):
            return await response.text()
    
    async def _parse_response_async(self, response: aiohttp.ClientResponse) -> Optional[Any]:
        """Parse non-binary async response content."""
        try:
            return await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError):
            return None
    
    
    
    async def text_to_speech(self, text: str, speaker_id: int,
                           enable_katakana_english: bool = True,
                           enable_interrogative_upspeak: bool = True,
                           core_version: Optional[str] = None,
                           speed_scale: float = 1.0,
                           pitch_scale: float = 0,
                           intonation_scale: float = 1.0,
                           volume_scale: float = 1.0,
                           pre_phoneme_length: float = 0.1,
                           post_phoneme_length: float = 0.1,
                           pause_length: Optional[float] = None,
                           pause_length_scale: float = 1.0) -> bytes:
        """Convert text directly to speech audio with customizable parameters (async).
        
        Args:
            text: Text to synthesize
            speaker_id: Speaker ID
            enable_katakana_english: Enable katakana pronunciation for English
            enable_interrogative_upspeak: Enable interrogative upspeak
            core_version: Optional specific core version
            speed_scale: Speech speed multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
            pitch_scale: Pitch adjustment multiplier (1.0 = normal)
            intonation_scale: Intonation strength multiplier (1.0 = normal)
            volume_scale: Volume multiplier (1.0 = normal)
            pre_phoneme_length: Silence duration before speech (seconds)
            post_phoneme_length: Silence duration after speech (seconds)
            pause_length: Optional pause length between phrases (seconds)
            pause_length_scale: Pause length multiplier (1.0 = normal)
            
        Returns:
            Audio data as bytes
        """
        # Create audio query directly via API
        query_params = {
            'text': text,
            'speaker': str(speaker_id),
            'enable_katakana_english': 'true' if enable_katakana_english else 'false'
        }
        if core_version:
            query_params['core_version'] = core_version
        
        response = await self._make_async_request('POST', '/audio_query', params=query_params)
        audio_query = AudioQuery(**response)
        
        # Apply custom parameters
        audio_query.speedScale = speed_scale
        audio_query.pitchScale = pitch_scale
        audio_query.intonationScale = intonation_scale
        audio_query.volumeScale = volume_scale
        audio_query.prePhonemeLength = pre_phoneme_length
        audio_query.postPhonemeLength = post_phoneme_length
        if pause_length is not None:
            audio_query.pauseLength = pause_length
        audio_query.pauseLengthScale = pause_length_scale
        
        # Synthesize directly via API
        synth_params = {
            'speaker': str(speaker_id),
            'enable_interrogative_upspeak': 'true' if enable_interrogative_upspeak else 'false'
        }
        if core_version:
            synth_params['core_version'] = core_version
            
        query_dict = self.serializer.serialize_audio_query(audio_query)
        
        return await self._make_async_request('POST', '/synthesis', params=synth_params,
                                            json_data=query_dict, return_binary=True)
    
    async def multi_synthesis_async(self, queries: List[AudioQuery], speaker: int,
                                   enable_interrogative_upspeak: bool = True,
                                   core_version: Optional[str] = None) -> bytes:
        params = {
            'speaker': str(speaker),
            'enable_interrogative_upspeak': 'true' if enable_interrogative_upspeak else 'false'
        }
        if core_version:
            params['core_version'] = core_version
            
        query_dicts = []
        for query in queries:
            query_dict = {
                'accent_phrases': query.accent_phrases,
                'speedScale': query.speedScale,
                'pitchScale': query.pitchScale,
                'intonationScale': query.intonationScale,
                'volumeScale': query.volumeScale,
                'prePhonemeLength': query.prePhonemeLength,
                'postPhonemeLength': query.postPhonemeLength,
                'outputSamplingRate': query.outputSamplingRate,
                'outputStereo': query.outputStereo
            }
            if query.kana:
                query_dict['kana'] = query.kana
            if query.pauseLength is not None:
                query_dict['pauseLength'] = query.pauseLength
            if query.pauseLengthScale != 1.0:
                query_dict['pauseLengthScale'] = query.pauseLengthScale
            query_dicts.append(query_dict)
            
        return await self._make_async_request('POST', '/multi_synthesis', params=params,
                                            json_data=query_dicts, return_binary=True)
    
    async def concurrent_text_to_speech(self, requests: List[TextToSpeechRequest], progress: bool = False) -> List[bytes]:
        """Convert multiple texts to speech concurrently with automatic batching.
        
        Args:
            requests: List of TextToSpeechRequest containing text_to_speech parameters.
                     Each request must have 'text' and 'speaker_id' keys, plus optional parameters.
            progress: Show progress bar using tqdm if True
                     
        Returns:
            List of audio data as bytes in the same order as input requests
            
        Example:
            requests: List[TextToSpeechRequest] = [
                {"text": "こんにちは", "speaker_id": 1},
                {"text": "ありがとう", "speaker_id": 2, "speed_scale": 0.8},
                {"text": "さようなら", "speaker_id": 1, "pitch_scale": 0.1}
            ]
            audio_list = await client.concurrent_text_to_speech(requests, progress=True)
        """
        if not requests:
            return []
            
        # Split requests into batches of 10
        batch_size = 10
        batches = [requests[i:i + batch_size] for i in range(0, len(requests), batch_size)]
        
        all_results = []
        
        # Initialize progress bar if requested
        progress_bar = None
        if progress:
            progress_bar = tqdm(total=len(requests), desc="Synthesizing audio", unit="audio")
        
        for batch in batches:
            # Create coroutines for the current batch
            coroutines = []
            for req in batch:
                # Extract parameters from request dict
                text = req['text']
                speaker_id = req['speaker_id']
                
                # Optional parameters with defaults
                params = {
                    'enable_katakana_english': req.get('enable_katakana_english', True),
                    'enable_interrogative_upspeak': req.get('enable_interrogative_upspeak', True),
                    'core_version': req.get('core_version'),
                    'speed_scale': req.get('speed_scale', 1.0),
                    'pitch_scale': req.get('pitch_scale', 0),
                    'intonation_scale': req.get('intonation_scale', 1.0),
                    'volume_scale': req.get('volume_scale', 1.0),
                    'pre_phoneme_length': req.get('pre_phoneme_length', 0.1),
                    'post_phoneme_length': req.get('post_phoneme_length', 0.1),
                    'pause_length': req.get('pause_length'),
                    'pause_length_scale': req.get('pause_length_scale', 1.0)
                }
                
                coroutines.append(self.text_to_speech(text, speaker_id, **params))
            
            # Execute batch concurrently with individual progress updates
            if progress_bar:
                # Create wrapper coroutines that update progress when done
                async def track_progress(coro):
                    result = await coro
                    progress_bar.update(1)
                    return result
                
                # Wrap each coroutine with progress tracking
                tracked_coroutines = [track_progress(coro) for coro in coroutines]
                batch_results = await asyncio.gather(*tracked_coroutines)
            else:
                batch_results = await asyncio.gather(*coroutines)
                
            all_results.extend(batch_results)
            
        # Close progress bar if it was created
        if progress_bar:
            progress_bar.close()
            
        return all_results

    def concurrent_text_to_speech_sync(self, requests: List[TextToSpeechRequest], progress: bool = False) -> List[bytes]:
        """Convert multiple texts to speech concurrently (synchronous interface).
        
        This method wraps the async concurrent_text_to_speech with asyncio.run
        so it can be called without explicit async/await.
        
        Args:
            requests: List of TextToSpeechRequest containing text_to_speech parameters.
                     Each request must have 'text' and 'speaker_id' keys, plus optional parameters.
            progress: Show progress bar using tqdm if True
                     
        Returns:
            List of audio data as bytes in the same order as input requests
            
        Example:
            client = VoiceVoxAsyncClient()
            requests: List[TextToSpeechRequest] = [
                {"text": "こんにちは", "speaker_id": 1},
                {"text": "ありがとう", "speaker_id": 2, "speed_scale": 0.8}
            ]
            audio_list = client.concurrent_text_to_speech_sync(requests, progress=True)
        """
        async def _run():
            async with self.__class__(api_key=self.api_key, base_url=self.base_url) as client:
                return await client.concurrent_text_to_speech(requests, progress=progress)
        
        return asyncio.run(_run())

    def save_audio(self, audio_data: bytes, filename: str) -> None:
        """Save audio data to file.
        
        Args:
            audio_data: Audio data bytes
            filename: Output filename
        """
        with open(filename, 'wb') as f:
            f.write(audio_data)


# Backward compatibility aliases
VoiceVoxClient = VoiceVoxSyncClient  # Main client defaults to sync for backward compatibility