from anc.api.connection import Connection
from requests.exceptions import RequestException
import os
import sys
import json
from rich.console import Console
from rich.table import Table, box
from rich.text import Text
import uuid
import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _format_and_print_logs(log_text):
    """Format and print workflow logs with better readability"""
    import re
    from datetime import datetime
    
    lines = log_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to parse JSON logs first
        if line.startswith('{"result":'):
            try:
                import json
                log_entry = json.loads(line)
                result = log_entry.get('result', {})
                content = result.get('content', '')
                pod_name = result.get('podName', '')
                
                if content:
                    # Extract and format timestamp if present in content
                    timestamp_match = re.search(r'time="([^"]+)"', content)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        try:
                            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%H:%M:%S')
                            content = re.sub(r'time="[^"]+" level=info msg="', f'[{formatted_time}] ', content)
                            content = re.sub(r'" argo=true.*$', '', content)
                        except:
                            pass
                    
                    print(content)
                elif not content and pod_name:
                    # Empty content but has podName, skip these empty entries
                    continue
                continue
            except:
                pass
        
        # Handle regular text logs
        # Extract and format timestamp if present
        timestamp_match = re.search(r'time="([^"]+)"', line)
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%H:%M:%S')
                line = re.sub(r'time="[^"]+" level=info msg="', f'[{formatted_time}] ', line)
                line = re.sub(r'" argo=true.*$', '', line)
            except:
                pass
        
        # Clean up common patterns and print
        # Remove excessive whitespace and format nicely
        if line.startswith('==='):
            print(f"\n{line}")
        elif line.startswith('ERROR:') or line.startswith('WARNING:'):
            print(f"⚠️  {line}")
        elif line.startswith('Successfully installed') or line.startswith('Saved'):
            print(f"✅ {line}")
        elif 'MB/s eta' in line or '━━━━━' in line:
            # Skip download progress bars
            continue
        elif line.startswith('[notice]'):
            print(f"ℹ️  {line}")
        else:
            print(line)

MM_BASE_URL = "http://model-management-service.infra.svc.cluster.local:5000"


def trigger_eval_job(
    run_id: str,
    model_name: str,
    project_name: str,
    ckpt_list: list[str],
    dataset_list: list[str],
    tp: int,
    pp: int,
    ep: int,
    seq_len: int,
    batch_size: int,
    tokenizer_path: str,
    validation_batch_size: int,
    dataset_tasks: str = None,
    model_args: str = None,
    wandb_project: str = None,
    wandb_api_key: str = None,
) -> bool:
    cluster = os.environ.get("MLP_CLUSTER", "il2")
    project = os.environ.get("MLP_PROJECT", "llm")
    
    data = {
        "evaluation_id": run_id,
        "modality": "nlp",
        "model_name": model_name,
        "project_name": project_name,
        "eval_ckpt_list": ckpt_list,
        "eval_dataset_list": dataset_list,
        "project": project,
        "cluster": cluster,
        "eval_tp": tp,
        "eval_pp": pp,
        "eval_ep": ep,
        "eval_seqlen": seq_len,
        "eval_batch_size": batch_size,
        "eval_tokenizer_path": tokenizer_path,
        "status": "start",
        "validation_batch_size": validation_batch_size,
    }
    
    # Add dataset_tasks to data if provided
    if dataset_tasks:
        data["eval_tasks"] = dataset_tasks
    
    if model_args:
        data["model_args"] = model_args
    
    if wandb_project and wandb_api_key:
        data["wandb_project"] = wandb_project
        data["wandb_api_key"] = wandb_api_key

    try:
        conn = Connection(url=MM_BASE_URL)
        response = conn.post("/evaluations", json=data)

        # Check if the status code is in the 2xx range
        if 200 <= response.status_code < 300:
            response_data = response.json()
            evaluation_id = response_data.get('evaluation_id')
            if evaluation_id:
                print(f"Evaluation task added successfully. Your Eval ID is: \033[92m{evaluation_id}\033[0m")
                print(f"You can check the status of your evaluation using: \033[96manc eval status {evaluation_id}\033[0m")
                print(f"All historical results can be viewed at: \033[94mhttp://model.anuttacon.ai/models/467e151d-a52a-47f9-8791-db9c776635db/evaluations\033[0m")
            else:
                print("Evaluation failed, didn't get the evaluation id")
        else:
            #print(f"Error: Server responded with status code {response.status_code}")
            print(f"{response.text}")

    except RequestException as e:
        print(f"Sorry, you can't add dataset out of clusters, please use it in a notebook")
    except json.JSONDecodeError:
        print("Sorry: received invalid JSON response from server")
    except KeyboardInterrupt:
        print(f"Operation interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Sorry, your command run failed, you can try again or reach out infra team")


def display_evaluation_status(evaluation_id: str):
    conn = Connection(url=MM_BASE_URL)
    response = conn.get(f"/evaluations/{evaluation_id}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Create a Rich console instance
        console = Console(width=200)  # Set wider console width
        
        # Display basic evaluation information
        eval_info = Table(title=f"Evaluation ID: {evaluation_id}", box=box.ROUNDED)
        eval_info.add_column("Parameter", style="cyan")
        eval_info.add_column("Value", style="green")
        
        # Add some key evaluation parameters
        eval_info.add_row("Model Name", data.get('model_name') or 'N/A')
        eval_info.add_row("Project", data.get('project') or 'N/A')
        eval_info.add_row("Submitted At", data.get('submitted_at') or 'N/A')
        
        console.print(eval_info)
        console.print()
        
        # Parse and display the evaluation_results_info
        if data.get('evaluation_results_info'):
            try:
                results_info = json.loads(data['evaluation_results_info'])
                
                # Create table for evaluation results with expanded width
                results_table = Table(title="Evaluation Results", box=box.ROUNDED, show_lines=True)
                results_table.add_column("Checkpoint", style="magenta", width=50, no_wrap=True)
                results_table.add_column("Dataset", style="blue", width=25, no_wrap=True)
                results_table.add_column("Endpoint URL", style="yellow", no_wrap=True)
                
                # Add rows for each checkpoint and dataset combination
                for ckpt_path, dataset_list in results_info.items():
                    # Get basename for the checkpoint
                    ckpt_basename = os.path.basename(ckpt_path)
                    
                    # Handle the case where each checkpoint has multiple datasets
                    for dataset_info in dataset_list:
                        if len(dataset_info) >= 4:
                            # Extract dataset info
                            dataset_path = dataset_info[0]
                            endpoint_url = dataset_info[1]
                            job_id = dataset_info[2]
                            status = dataset_info[3]
                            
                            # Get basename for dataset
                            dataset_basename = os.path.basename(dataset_path)
                            
                            results_table.add_row(
                                ckpt_basename,
                                dataset_basename,
                                endpoint_url
                            )
                
                # Ensure the table doesn't truncate content
                console.print(results_table)
            except json.JSONDecodeError:
                console.print(f"[red]Error parsing evaluation results info: {data['evaluation_results_info']}[/red]")
        else:
            console.print("[yellow]No evaluation results information available.[/yellow]")
    else:
        console.print(f"[red]Error retrieving evaluation status: {response.text}[/red]")


def trigger_eval_sweep(spec: dict, cluster, project, run_id=None):
    if run_id is None:
        
        run_id = str(uuid.uuid4())

    cluster = os.environ.get("MLP_CLUSTER", "il2")
    project = os.environ.get("MLP_PROJECT", "llm")
    config = None
    try:
        with open(spec, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {spec}: \n {e}")
        return

    if config is None or len(config) == 0:
        print("YAML file is empty or invalid.")
        return

    data = {
        "evaluation_id": run_id,
        "spec": config,
        "cluster": cluster,
        "project": project,
        "model_name": "sweep",
    }
    try:
        conn = Connection(url=MM_BASE_URL)
        response = conn.post("/evaluations", json=data)

        # Check if the status code is in the 2xx range
        if 200 <= response.status_code < 300:
            response_data = response.json()
            evaluation_id = response_data.get('evaluation_id')
            if evaluation_id:
                print(f"Sweep workflow submmited. you can use the highlight command: \033[92manc eval log {evaluation_id}\033[0m to check the logs")
            else:
                print("Evaluation failed, didn't get the evaluation id")
        else:
            #print(f"Error: Server responded with status code {response.status_code}")
            print(f"{response.text}")

    except RequestException as e:
        print(f"Sorry, you can't add dataset out of clusters, please use it in a notebook")
    except json.JSONDecodeError:
        print("Sorry: received invalid JSON response from server")
    except KeyboardInterrupt:
        print(f"Operation interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Sorry, your command run failed, you can try again or reach out infra team")


def eval_log_print(evaluation_id, cluster):
    namespace = "argo"

    # First, get workflow_name from evaluation service
    conn = Connection(url=MM_BASE_URL)
    response = conn.get(f"/evaluations/{evaluation_id}")
    
    if response.status_code != 200:
        print(f"Failed to get evaluation info: HTTP {response.status_code} {response.text}")
        return
    
    try:
        data = response.json()
        workflow_name = data.get('train_job_url')
        if not workflow_name or workflow_name.startswith("http"):
            print(f"No workflow found for evaluation {evaluation_id}.")
            return
        
        print(f"Found workflow: {workflow_name} for evaluation {evaluation_id}")
    except Exception as e:
        print(f"Failed to parse evaluation response: {e}")
        return

    def _resolve_argo_server_url(cluster_name):
        if cluster_name == "il2":
            return "https://10.218.61.160"
        elif cluster_name == "hb":
            return "https://10.53.139.209"

        raise ValueError(f"Unsupported cluster: {cluster_name} for argo server url")
    
    base_url = _resolve_argo_server_url(cluster)
    print(f"Debug: Using Argo server URL: {base_url}")

    # 1) Get workflow to discover nodes/pods
    wf_url = f"{base_url}/api/v1/workflows/{namespace}/{workflow_name}"
    try:
        wf_resp = requests.get(wf_url, verify=False)
    except Exception as e:
        print(f"Failed to connect to Argo server: {e}")
        return

    if wf_resp.status_code != 200:
        print(f"Failed to get workflow: HTTP {wf_resp.status_code} {wf_resp.text}")
        return

    try:
        wf = wf_resp.json()
    except Exception as e:
        print(f"Failed to parse workflow JSON: {e}")
        return

    status = wf.get('status', {})
    nodes = status.get('nodes', {}) or {}
    print(f"Debug: Found {len(nodes)} nodes in workflow status")
    
    # Check if nodes are offloaded
    if status.get('offloadNodeStatusVersion'):
        print(f"Debug: Nodes are offloaded (version: {status.get('offloadNodeStatusVersion')})")
        # Try to get nodes from separate endpoint
        nodes_url = f"{base_url}/api/v1/workflows/{namespace}/{workflow_name}/nodes"
        try:
            nodes_resp = requests.get(nodes_url, verify=False)
            if nodes_resp.status_code == 200:
                nodes_data = nodes_resp.json()
                nodes = nodes_data.get('items', [])
                print(f"Debug: Retrieved {len(nodes)} nodes from nodes endpoint")
                # Convert list to dict format
                if isinstance(nodes, list):
                    nodes_dict = {}
                    for node in nodes:
                        node_id = node.get('id', '')
                        if node_id:
                            nodes_dict[node_id] = node
                    nodes = nodes_dict
        except Exception as e:
            print(f"Debug: Failed to get nodes from separate endpoint: {e}")

    logs_url = f"{base_url}/api/v1/workflows/{namespace}/{workflow_name}/log"

    # 2) Try aggregated workflow logs first (covers all steps/pods)
    print("Debug: Trying aggregated logs...")
    try:
        # Try different parameter combinations
        param_variants = [
            {},  # No parameters
            {"logOptions.follow": "false"},
            {"follow": "false"},
            {"logOptions.container": "main"},
        ]
        
        for params in param_variants:
            agg_resp = requests.get(logs_url, params=params, verify=False)
            print(f"Debug: Aggregated logs attempt with params {params}: HTTP {agg_resp.status_code}")
            if agg_resp.status_code == 200 and agg_resp.text.strip():
                print("==== Aggregated Workflow Logs ====")
                _format_and_print_logs(agg_resp.text)
                return
    except Exception as e:
        print(f"Debug: Aggregated logs failed: {e}")

    # 3) Try per-node logs using nodeId
    node_items = []
    for node_id, node in nodes.items():
        node_items.append({
            "id": node_id,
            "displayName": node.get("displayName") or node.get("name") or node_id,
            "type": node.get("type"),
            "finishedAt": node.get("finishedAt") or node.get("startedAt") or "",
            "podName": node.get("podName")
        })
    
    print(f"Debug: Processing {len(node_items)} nodes for individual logs")
    # sort by finishedAt for deterministic order
    node_items.sort(key=lambda x: x.get("finishedAt") or "")

    printed_any = False
    for item in node_items:
        print(f"Debug: Trying logs for node {item['displayName']} ({item['type']})")
        
        # Try different parameter combinations for individual nodes
        params_variants = [
            {"nodeId": item["id"]},
            {"nodeId": item["id"], "logOptions.follow": "false"},
            {"nodeId": item["id"], "follow": "false"},
            {"nodeId": item["id"], "logOptions.container": "main"},
        ]
        
        if item.get("podName"):
            params_variants.extend([
                {"podName": item["podName"]},
                {"podName": item["podName"], "logOptions.container": "main"},
                {"podName": item["podName"], "container": "main"},
            ])

        log_text = None
        last_err = None
        for params in params_variants:
            try:
                resp = requests.get(logs_url, params=params, verify=False)
                if resp.status_code == 200 and resp.text.strip():
                    log_text = resp.text
                    break
                else:
                    last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as e:
                last_err = str(e)

        if log_text:
            printed_any = True
            print("")
            print(f"==== Step: {item['displayName']} ({item['type']}) ====")
            _format_and_print_logs(log_text)
        else:
            print(f"Debug: No logs found for {item['displayName']}: {last_err}")

    if not printed_any:
        print("No logs found for this workflow.")
    