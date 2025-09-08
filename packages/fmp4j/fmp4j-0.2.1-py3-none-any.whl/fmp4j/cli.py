def check_jvm():
    """Check if JVM is properly configured"""
    try:
        import jpype
        print("✅ JPype is installed")

        if jpype.isJVMStarted():
            print("✅ JVM is running")
        else:
            print("ℹ️ JVM is not started yet")

    except ImportError:
        print("❌ JPype is not installed")