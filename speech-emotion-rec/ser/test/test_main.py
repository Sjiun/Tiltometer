import wave

import numpy as np
import pytest

from ser import main


@pytest.mark.asyncio
async def test_get_ser_result_from_server_message():
    # Arrange
    audio_array = load_wav_file('test.wav')
    target_length = 6 * 48000  # 6 seconds * 48 kHz
    padded_audio_array = pad_array(audio_array, target_length)
    padded_f32_audio_array = padded_audio_array.astype(np.float32, order='C') / 32767.0

    chunk_size = 4096
    audio_chunks = [
        padded_f32_audio_array[i:i + chunk_size] for i in range(0, len(padded_f32_audio_array), chunk_size)
    ]
    result_is_not_none_counter = 0

    # Act
    for chunk in audio_chunks:
        result = await main.get_ser_result_from_server_message(chunk)

        # Assert
        if result is not None:
            result_is_not_none_counter += 1
            assert ['angry', 'happy', 'neutral', 'sad', 'surprise'] == list(result.keys())
            assert all(isinstance(v, float) for v in result.values())

    # 6 seconds input; predictions are made every second after 4 seconds are reached
    assert 3 == result_is_not_none_counter


def load_wav_file(file_name: str) -> np.ndarray:
    with wave.open(file_name, 'rb') as wav_file:
        n_frames = wav_file.getnframes()
        audio_bytes = wav_file.readframes(n_frames)
        return np.frombuffer(audio_bytes, dtype=np.int16)


def pad_array(audio_array: np.ndarray, target_length: int) -> np.ndarray:
    if len(audio_array) >= target_length:
        return audio_array[:target_length]

    pad_len = target_length - len(audio_array)
    pad_rem = pad_len % 2
    pad_len //= 2
    return np.pad(audio_array, (pad_len, pad_len + pad_rem), 'constant', constant_values=0)
