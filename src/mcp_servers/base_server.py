"""
Base MCP server implementation.
"""
from fastmcp import FastMCP
from utils.logging import setup_logging

class BaseMCPServer:
    """Base class for MCP servers."""
    
    def __init__(self, name: str, port: int, description: str):
        self.name = name
        self.port = port
        self.description = description
        self.logger = setup_logging(f"MCP.{name}")
        self.mcp = FastMCP(name)
        
    def register_tools(self):
        """Override this method to register server-specific tools."""
        raise NotImplementedError("Subclasses must implement register_tools()")
        
    # REPLACED async def start(self)
    def _start_and_run_mcp_blocking(self):
        try:
            self.logger.info(f"({self.name}) Preparing to start MCP server (blocking call)...")
            self.register_tools()
            self.logger.info(f"({self.name}) Calling self.mcp.run() (blocking)...")
            # Assuming self.mcp.run() is a synchronous, blocking call.
            # If it's a coroutine, this will cause a "coroutine was never awaited" warning
            # and the server likely won't run correctly.
            self.mcp.run(port=self.port, transport="streamable-http") # NO AWAIT
            # If mcp.run is a server, it will block here until stopped.
            self.logger.info(f"({self.name}) self.mcp.run() (blocking) apparently finished.")
        except Exception as e:
            self.logger.error(f"({self.name}) Error in _start_and_run_mcp_blocking: {e}", exc_info=True)
            raise # Re-raise to be caught by the thread's exception handler in run()

    def run(self):
        """Run the server (blocking). This method itself is synchronous."""
        import threading
        
        result = {"exception": None}
        
        # This function will be the target for the new thread.
        def server_thread_target():
            try:
                self.logger.info(f"Thread for {self.name}: Starting server via _start_and_run_mcp_blocking.")
                self._start_and_run_mcp_blocking()
                # If _start_and_run_mcp_blocking returns (e.g., server stopped gracefully), log it.
                self.logger.info(f"Thread for {self.name}: _start_and_run_mcp_blocking completed without error.")
            except Exception as e:
                self.logger.error(f"Thread for {self.name}: Exception caught from _start_and_run_mcp_blocking: {e}", exc_info=True)
                result["exception"] = e
        
        server_thread = threading.Thread(target=server_thread_target, daemon=True, name=f"{self.name}ServerThread")
        self.logger.info(f"Main thread (in BaseMCPServer.run for {self.name}): Starting server thread.")
        server_thread.start()
        
        try:
            self.logger.info(f"Main thread (in BaseMCPServer.run for {self.name}): Joining server thread.")
            # Keep the main thread alive, allowing the server_thread (daemon) to run.
            # The join will block until server_thread terminates.
            server_thread.join() 
            self.logger.info(f"Main thread (in BaseMCPServer.run for {self.name}): Server thread joined.")
            if result["exception"]:
                self.logger.error(f"Main thread: Server {self.name} failed due to an exception in its thread: {result['exception']!r}. Re-raising.")
                raise result["exception"]
            self.logger.info(f"Main thread: Server thread for {self.name} appears to have finished.")
        except KeyboardInterrupt:
            self.logger.info(f"Main thread: KeyboardInterrupt received. Stopping {self.name} server. Daemon thread will exit.")
            # server_thread is a daemon, so it will be terminated when the main program exits.
            # If self.mcp.run() needs explicit cleanup on KeyboardInterrupt, 
            # it should ideally handle SIGINT or have a specific stop method.
        except Exception as e:
            self.logger.error(f"Main thread: Fatal error in BaseMCPServer.run for {self.name}: {e}", exc_info=True)
            raise
