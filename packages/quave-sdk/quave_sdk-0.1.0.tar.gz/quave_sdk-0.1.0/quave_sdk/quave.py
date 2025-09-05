import requests
import warnings
import time
from qiskit import QuantumCircuit
from qiskit.result import Result
from qiskit.visualization import plot_histogram
import asyncio
from supabase import create_client, Client, acreate_client, AClient, FunctionsError
from typing import Any, Callable
import getpass

class Result():
    id: str
    user_id: str
    counts: dict[str, int]
    parameters: dict[str, float]
    status: str
    executed_at: str
    backend_version: str | None
    hardware_id: str | None
    qasm: str
    shots: int
    error: str | None
    provider: str

    def __init__ (
            self, 
            id: str, 
            user_id: str, 
            counts: dict[str, int],
            parameters: dict[str, float],
            status: str, 
            executed_at: str, 
            backend_version: str, 
            hardware_id: str, 
            qasm: str, 
            shots: int, 
            error: str, 
            provider: str):
        self.id = id
        self.user_id = user_id
        self.counts = counts
        self.parameters = parameters
        self.status = status
        self.executed_at = executed_at
        self.backend_version = backend_version
        self.hardware_id = hardware_id
        self.qasm = qasm
        self.shots = shots
        self.error = error
        self.provider = provider


class Quave:
    default_backend = "simulate"
    default_provider = "simulator"

    def __init__(self, email: str | None = None, password: str | None = None):
        # If email is not provided, ask interactively
        if not isinstance(email, str) or not email.strip():
            email = input("Enter your email: ").strip()

        # If password is not provided, ask securely
        if not isinstance(password, str) or not password.strip():
            password = getpass.getpass("Enter your password: ")
        
        self.supabase: Client = create_client("https://dykixucbxclbrwdvrgfx.supabase.co", "sb_publishable__zGmHDukGharhEpZd1NOgg_vpnZHnSx")
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        self.realtime: AClient = asyncio.run(acreate_client("https://dykixucbxclbrwdvrgfx.supabase.co", "sb_publishable__zGmHDukGharhEpZd1NOgg_vpnZHnSx"))
        a_response = asyncio.run(self.realtime.auth.sign_in_with_password({
            "email": email,
            "password": password
        }))

        self.base_url = "https://api.quave.qaion.com"

        if not response.session or not a_response:
            raise Exception("Authentication failed - invalid credentials")

    @staticmethod
    def _compile_to_ir(circuit: QuantumCircuit) -> str:
        """
        Transpile `circuit` and return an OpenQASM3 representation.
        
        Args:
            circuit (QuantumCircuit): quantum circuit to transpile to QASM3

        Returns:
            str: qasm3 string representation of the circuit
        """

        try:
            from qiskit import transpile, qasm3
        except Exception as exc:  # pragma: no cover - qiskit missing
            raise ImportError("qiskit is required for compiling circuits") from exc

        basis = ["u", "cx", "measure"]  # QASM3 prefers 'u' over u1/u2/u3
        try:
            tcirc = transpile(circuit, basis_gates=basis, optimization_level=1)
        except Exception:  # pragma: no cover - transpile failures
            tcirc = circuit
        
        return qasm3.dumps(tcirc)

    
    @staticmethod
    def _json_to_result(result: dict[str, Any]) -> Result:

        return Result(
            id=result.get("id", None),
            user_id = result.get("user_id", None),
            counts = result.get("counts", None),
            status = result.get("status", None),
            parameters = result.get("parameters", None),
            executed_at = result.get("executed_at", None),
            backend_version = result.get("backend_version", None),
            hardware_id = result.get("hardware_id", None),
            qasm = result.get("qasm", None),
            shots = result.get("shots", None),
            error = result.get("error", None),
            provider = result.get("provider", None)
        )

    def _validate_supabase_session(self):
        """
        Automatically refreshes supabase session if expired.
        Call this before making Supabase API calls to ensure valid session
        """

        expiration_buffer = 60

        if self.supabase.auth.get_session().expires_at - expiration_buffer <= int(time.time()):

            refreshed = self.supabase.auth.refresh_session()
            if not refreshed or not refreshed.session:
                raise Exception("Session refresh failed. Please log in again.")
        
    async def _validate_realtime_session(self):
        """
        Automatically refreshes supabase realtime session if expired.
        Call this before making Supabase realtime API calls to ensure valid session
        """
        
        expiration_buffer = 60

        session = await self.realtime.auth.get_session()
        if session.expires_at - expiration_buffer <= int(time.time()):
            refreshed = await self.realtime.auth.refresh_session()
            if not refreshed or not refreshed.session:
                raise Exception("Session refresh failed. Please log in again.")

    def execute(self, circuit: QuantumCircuit, parameters: dict[str, float] = None, shots: int = 1024, backend: str = default_backend) -> str:
        """
        Queues circuit for execution with the specified backend and the assigned parameters.

        Args:
            circuit (QuantumCircuit): The circuit to be executed
            parameters (Dict[str, float]): The value of parameters in the circuit, assigned in the positional order of circuit.parameters (alphabetically) - default = None
            shots (int): The number of shots for the circuit to execute - default = 1024
            backend (str): The backend for the circuit to execute on - default = "simulate"

        Returns:
            str: id of the result
        
        Raises:
            RuntimeError: If Quave failed to queue the job with the specified backend
            ValueError: If the number of parameters provided are not the same
            Exception: If there was an error sending the request or storing the job metadata
        """

        try:

            provider = Quave.default_provider

            if backend != Quave.default_backend:
                provider = None
                # Check whether the backend is supported
                supported_backends = self.list_backends()
                if not supported_backends:
                    warnings.warn("Failed to fetch supported backends so unable to validate backend", FutureWarning)
                else:
                    for backend_provider, backend_list in supported_backends.items():
                        if backend in backend_list:
                            provider = backend_provider
                    if not provider:
                        warnings.warn("Backend not supported. Defaulting to Aer simulator", FutureWarning)
                        backend = Quave.default_backend
                        provider = Quave.default_provider

            num_params = len(circuit.parameters)
            num_args = 0 if not parameters else len(parameters)
            if num_params != num_args:
                raise ValueError(f"The number of parameters in the circuit ({num_params}) was not equal to the number of parameters provided ({num_args})")

            self._validate_supabase_session()
            qasm = self._compile_to_ir(circuit)
            user_id = self.supabase.auth.get_user().user.id

            payload = {
                "qasm": qasm,
                "parameters": parameters,
                "shots": shots,
                "backend": backend
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.supabase.auth.get_session().access_token}"
            }

            url = f"{self.base_url}/v1/jobs"

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            resp_json = response.json()
            print(resp_json) # DEBUG
            if resp_json.get("status", "") != "accepted":
                raise RuntimeError(f"Failed to queue job: {resp_json.get('message', 'Unknown error')}")
            job_id = resp_json.get("job_id")
            
            response = (
                self.supabase.table("execution_results")
                .insert({
                    "id": job_id,
                    "user_id": user_id,
                    "status": "PENDING",
                    "qasm": qasm,
                    "parameters": parameters,
                    "shots": shots,
                    "backend_name": backend,
                    "provider": provider,
                })
                .execute()
            )

            return job_id

        except FunctionsError as e:
            raise Exception(f"Failed to execute circuit: {e.message}")
        except Exception as e:
            raise Exception(e)
        
    async def iterative_execute(
            self, 
            circuit: QuantumCircuit, 
            parameter_update_fn: Callable[[dict[str, int]], dict[str, float]], 
            initial_parameters: dict[str, float], 
            num_iterations: int = 10, 
            shots: int = 1024, 
            backend: str = default_backend, 
            timeout: float = 10000
    ) -> list[str | None]:
        """
        Iteratively executes circuit with the specified backend and the assigned parameters, updating parameters after each iteration.

        Args:
            circuit (QuantumCircuit): The circuit to be executed
            parameter_update_fn (Callable[[dict[str, int]], dict[str, float]]): Function which takes the shots as arguments and returns the new set of parameters
            initial_parameters (dict[str, float]): The value of parameters in the circuit's first iteration, assigned in the positional order of circuit.parameters (alphabetically)
            num_iterations (int): The number of iterations of the circuit with updated parameters - default = 10
            shots (int): The number of shots for the circuit to execute per parameter set - default = 1024
            backend (str): The backend for the circuit to execute on - default = "simulate"
            timout (float): Amount of seconds to wait before exiting without a result - default = 10000

        Returns:
            list[str]: List of Ids of each iteration result, with None for any results with an error (and any subsequent results)
        
        Raises:
            RuntimeError: If Quave failed to queue the job with the specified backend
            ValueError: If the number of parameters provided are not the same
            Exception: If there was an error sending the request or storing the job metadata
        """

        result_ids = [None] * num_iterations
        parameters = initial_parameters

        for i in range(num_iterations):
            result_ids[i] = self.execute(circuit, parameters, shots, backend)
            print("Finished running result: " + result_ids[i]) # DEBUG
            if i < num_iterations - 1:
                result = await self.await_result(result_ids[i], timeout)
                if not result:
                    warnings.warn(f"Timed out on iteration {i+1}", UserWarning)
                    return result_ids
                elif result.status == "COMPLETED" and result.counts:
                    print(f"Result: {result.counts}") # DEBUG
                    parameters = parameter_update_fn(result.counts)
                else:
                    print("Result status: " + result.status) # DEBUG
                    warnings.warn(f"Unable to retrieve counts for iteration {i+1}", RuntimeWarning)
                    return result_ids
                
        return result_ids
    
    def check_status(self, result_id: str) -> str:
        """
        Checks the status of a queued job.

        Args:
            result_id (str): Id of a queued job (received from .execute() method)

        Returns:
            str: Status of the job ("PENDING", "FAILED", or "COMPLETED")
        """
        try:
            self._validate_supabase_session()

            response = (
                self.supabase.table("execution_results")
                .select("*")
                .eq("id", result_id)
                .execute()
            )

            return response.data[0]["status"]

        except FunctionsError as e:
            raise Exception(f"Failed to check result status: {e.message}")
        except Exception as e:
            raise Exception(e)

    def get_result(self, result_id: str):
        """
        Retrieves the result of a queued job.

        Args:
            result_id (str): Id of a queued job (received from .execute() method)

        Returns:
            Result: Result of the job if it is complete
            None: If the result has not completed
        """

        if not isinstance(result_id, str):
            raise TypeError("result_id must be of type string")
        
        try:
            self._validate_supabase_session()

            response = (
                self.supabase.table("execution_results")
                .select("*")
                .eq("id", result_id)
                .execute()
            )

            result = self._json_to_result(response.data[0])

            if result.status != "PENDING":
                return result
            else:
                return None

        except FunctionsError as e:
            raise Exception(f"Failed to check result status: {e.message}")
        except Exception as e:
            raise Exception(e)
        
    

    async def await_result(self, result_id: str, timeout: float = 1000.0):
        """
        Waits for a job to be complete and then returns result asynchronously.

        Args:
            result_id (str): Id of a queued job (received from .execute() method)
            timout (float): Amount of seconds to wait before exiting without a result - default = 10000

        Returns:
            Result: Result of the job if it is complete
            None: If the result has not completed
        """

        await self._validate_realtime_session()

        loop = asyncio.get_running_loop()
        future: Result = loop.create_future()

        def on_update(payload):
            new_data = payload.get("data")
            if new_data and new_data.get("record").get("id") == result_id:
                if not future.done():
                    result = new_data.get("record")
                    future.set_result(self._json_to_result(result))

        # Subscribe to updates on the results table
        channel = (
            await self.realtime.channel("result_updates")
            .on_postgres_changes(
                "UPDATE", 
                schema="public", 
                table="execution_results", 
                filter=f"id=eq.{result_id}", 
                callback=on_update
            )
            .subscribe()
        )

        try:
            current = self.get_result(result_id)
            if current:
                return current
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            print(f"Timeout waiting for result {result_id}")
            return None
        finally:
            await self.realtime.remove_channel(channel)


    def visualize(result: Result):
        """Display a simple histogram of the result."""
        counts = result.get_counts()
        return plot_histogram(counts)

    def list_backends(self, provider: str = "all") -> dict[str, list[str]] | list[str] | None:
        """
        Fetches a list of all available quantum backends grouped by provider.

        Args:
            provider (str): provider to retrieve backends for (default of "all")

        Returns:
            dict[provider: str, list[backend: str]]: Providers mapped to lists of backend names if provider is None
            list[backend: str]: List of backend names for a given provider if provider argument is specified
            None: if provider does not exist
        """

        self._validate_supabase_session()
        url = f"{self.base_url}/v1/backends"
        
        headers = {
            "Authorization": f"Bearer {self.supabase.auth.get_session().access_token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        backends = response.json()
        
        if provider == "all":
            return backends
        elif provider in backends:
            return backends[provider]
        else:
            return None

    def get_backend_stats(self, backend_name: str, provider: str):
        """
        Fetches statistics and configuration for a specific backend.

        Args:
            backend_name (str): The backend identifier (if none or incorrect value provided, assumes IBM).
        
        Returns:
            dict: Backend statistics and configuration.
            None: if backend does not exist
        """
        if provider not in ["simulator", "ibm", "braket", "custom"]:
            warnings.warn(f"Provider {provider} not supported. Defaulting to simulator")
            provider = "simulator"
        
        self._validate_supabase_session()
        url = f"{self.base_url}/v1/backends/statistics"
        
        params = {"backend": backend_name, "provider": provider}
        headers = {
            "Authorization": f"Bearer {self.supabase.auth.get_session().access_token}"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None
        return response.json()