import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square } from 'lucide-react';

const VoiceRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [message, setMessage] = useState<string>('');
  const [transcribedText, setTranscribedText] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [displayedText, setDisplayedText] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const dataChunksRef = useRef<Blob[]>([]);
  const streamTextRef = useRef<string>('');
  const streamIndexRef = useRef<number>(0);

  useEffect(() => {
    if (transcribedText && transcribedText !== streamTextRef.current) {
      
      const newText = transcribedText.slice(streamTextRef.current.length);
      streamTextRef.current = transcribedText;
      streamIndexRef.current = 0;
      
      if (newText) {
        setIsStreaming(true);
        
        const streamText = () => {
          if (streamIndexRef.current < newText.length) {
            setDisplayedText(prev => prev + (newText[streamIndexRef.current] || ''));
            streamIndexRef.current++;
            setTimeout(streamText, 50);
          } else {
            setIsStreaming(false);
          }
        };

        streamText();
      }
    }
  }, [transcribedText]);

  const startRecording = async (): Promise<void> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      mediaRecorderRef.current = mediaRecorder;

      dataChunksRef.current = [];
   

      mediaRecorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) {
          dataChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        try {
          setIsProcessing(true);
          const blob = new Blob(dataChunksRef.current, { type: 'audio/webm' });
          setAudio(blob);
          await uploadAudio(blob);
        } catch (error) {
          console.error('Error processing audio:', error);
          setMessage('Error processing audio. Please try again.');
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start(1000);
      setIsRecording(true);
      setMessage('Recording in progress...');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setMessage('Error accessing microphone.');
    }
  };

  const stopRecording = (): void => {
    const mediaRecorder = mediaRecorderRef.current;
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setMessage('Processing recording...');
    }
  };

  const uploadAudio = async (audioBlob: Blob | null): Promise<void> => {
    if (!audioBlob) {
      setMessage('No audio to upload.');
      return;
    }

    const formData = new FormData();
    const file = new File([audioBlob], 'recording.webm', {
      type: 'audio/webm',
      lastModified: new Date().getTime()
    });
    
    formData.append('audio', file);

    try {
      const response = await fetch('/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const textResponse = await response.text();
      
      if (!textResponse) {
        throw new Error('Empty response from server');
      }

      let data;
      try {
        data = JSON.parse(textResponse);
      } catch {
        data = textResponse;
      }

      if (data) {
        setTranscribedText(prev => 
          prev ? `${prev}\n${data}` : data
        );
        setMessage('Transcription successful');
      } else {
        setMessage('No transcription text received');
      }
    } catch (error) {
      console.error('Error uploading audio:', error);
      if (error instanceof Error) {
        setMessage(`Upload failed: ${error.message}`);
      } else {
        setMessage('Upload failed. Please try again.');
      }
    }
  };

  const handleRecordingClick = (): void => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-emerald-800">
      {!isRecording && (
        <div className="mb-10">
          <p className="text-white text-2xl font-bold mb-4">How can we assist you today?</p>
        </div>
      )}

      {isRecording && (
        <div className="flex gap-4 mb-12">
          {[0, 1, 2, 3, 4].map((index) => (
            <div
              key={index}
              className="wave-dot w-8 h-8 bg-white rounded-full transition-transform duration-100"
              style={{
                animationDelay: `${index * 250}ms`
              }}
            />
          ))}
        </div>
      )}
      
      <div className="flex flex-col items-center gap-10">
        <button
          onClick={handleRecordingClick}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          disabled={isProcessing}
          className={`
            p-4
            rounded-full
            transition-all
            duration-200
            ${isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-white hover:bg-gray-200'}
            ${isHovered ? 'scale-110' : 'scale-100'}
            ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          {isRecording ? (
            <Square className="w-8 h-8 text-white"/>
          ) : (
            <Mic className={`w-8 h-8 ${isRecording ? 'text-white' : 'text-emerald-800'}`} />
          )}
        </button>

        {displayedText && (
          <div className="w-[45%] bg-white rounded-lg p-4 shadow-lg fixed bottom-10">
            <div className="h-[70px] overflow-y-auto text-black-700 text-sm custom-scrollbar">
              {displayedText}
              {isStreaming && (
                <span className="w-4 h-4 bg-emerald-500 rounded-full inline-block ml-1 animate-pulse"/>
              )}
            </div>
          </div>
        )}
      </div>

      <style>
        {`
          @keyframes wave {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-28px); }
          }

          .wave-dot {
            animation: wave 2s infinite;
          }

          .custom-scrollbar {
            scrollbar-width: thin;
            scrollbar-color: #4ade80 #ffffff;
          }

          .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
          }
          
          .custom-scrollbar::-webkit-scrollbar-track {
            background: #ffffff;
            border-radius: 3px;
          }
          
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background-color: #4ade80;
            border-radius: 3px;
          }
        `}
      </style>
    </div>
  );
};

export default VoiceRecorder;