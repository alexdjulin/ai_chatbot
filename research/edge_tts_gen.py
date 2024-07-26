import os
import edge_tts
import asyncio
import playsound

TEXT = "Carpe Diem, seize the day!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"

async def amain() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(amain())
    playsound.playsound(OUTPUT_FILE)
    os.remove(OUTPUT_FILE)
