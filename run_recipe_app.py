#!/usr/bin/env python3
"""
Wrapper script to run AxiumGPT with proper environment setup
This helps avoid library conflicts with Streamlit
"""

import os
import sys
import subprocess

def main():
    """Run AxiumGPT with proper environment"""
    
    # Set environment variables to help with library compatibility
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Disable some features that can cause conflicts
    os.environ["PYTORCH_JIT"] = "0"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # Help with Google libraries import
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"
    
    print("🚀 Starting AxiumGPT...")
    print("🔧 Setting up environment for library compatibility...")
    
    try:
        # Run streamlit with the app
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            #"axiumgpt_chatbot.py",
            "recipe_generator5.py",
            "--server.fileWatcherType", "none",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ]
        
        print(f"🏃 Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check your .env file has GEMINI_API_KEY")
        print("   3. Try running: python axiumgpt.py directly to test imports")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Shutting down AxiumGPT gracefully...")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())