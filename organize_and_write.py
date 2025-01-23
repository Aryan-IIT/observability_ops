import json
from datetime import datetime

class LogProcessor:
    def __init__(self, output_file):
        self.output_file = output_file
        self.log_entries = []

    def process_event(self, event):
        try:
            # Parse event details
            timestamp = event.get('Timestamp', 'N/A')
            model = event.get('Model', 'unknown')
            prompt = event.get('Prompt', 'N/A')
            completion = event.get('Completion', 'N/A')

            # Extract metadata from completion if it's a structured object
            completion_text = "N/A"
            completion_tokens = "N/A"
            total_tokens = "N/A"
            if isinstance(completion, dict):
                import json
                from datetime import datetime

                def parse_completion(completion):
                    """
                    Parse the completion object to extract relevant metadata and organize it into a dictionary.
                    """
                    metadata = {
                        "chat": {
                            "prompt": completion.get("choices", [{}])[0].get("message", {}).get("content", "N/A"),
                            "response": completion.get("choices", [{}])[0].get("message", {}).get("content", "N/A"),
                        },
                        "model_details": {
                            "model": completion.get("model", "Unknown"),
                            "id": completion.get("id", "N/A"),
                            "system_fingerprint": completion.get("system_fingerprint", "N/A"),
                        },
                        "usage": {
                            "completion_tokens": completion.get("usage", {}).get("completion_tokens", 0),
                            "prompt_tokens": completion.get("usage", {}).get("prompt_tokens", 0),
                            "total_tokens": completion.get("usage", {}).get("total_tokens", 0),
                        },
                        "choices": [
                            {
                                "index": choice.get("index", -1),
                                "finish_reason": choice.get("finish_reason", "N/A"),
                                "message_content": choice.get("message", {}).get("content", "N/A"),
                            }
                            for choice in completion.get("choices", [])
                        ],
                        "timestamps": {
                            "created": datetime.utcfromtimestamp(completion.get("created", 0)).isoformat(),
                            "logged": datetime.utcnow().isoformat(),
                        },
                    }
                    return metadata

                def write_metadata_to_file(metadata, output_file="metadata_output.json"):
                    """
                    Write the extracted metadata to a JSON file for easy review and processing.
                    """
                    with open(output_file, "w") as f:
                        json.dump(metadata, f, indent=4)

                def main(completion_data):
                    """
                    Main function to parse the completion data and write metadata to a file.
                    """
                    metadata = parse_completion(completion_data)
                    write_metadata_to_file(metadata)
                    print(f"Metadata successfully written to 'metadata_output.json'.")

                # Example usage:
                # Replace `example_completion_data` with your actual completion data object.
                example_completion_data = {
                    "id": "chatcmpl-AihHMMlqFSMYhEY0SpE7jo9yHg6oR",
                    "created": 1735216160,
                    "model": "gpt-4o-mini-2024-07-18",
                    "system_fingerprint": "fp_04751d0b65",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "index": 0,
                            "message": {"content": "I now can give a great answer", "role": "assistant"},
                        }
                    ],
                    "usage": {"completion_tokens": 533, "prompt_tokens": 303, "total_tokens": 836},
                }

         
                usage = completion.get('usage', {})
                completion_tokens = usage.get('completion_tokens', 'N/A')
                total_tokens = usage.get('total_tokens', 'N/A')

            # Append processed log
            log_entry = {
                'Timestamp': timestamp,
                'Model': model,
                'Prompt': prompt,
                'Completion': completion_text.strip(),
                'CompletionTokens': completion_tokens,
                'TotalTokens': total_tokens,
            }
            self.log_entries.append(log_entry)
        except Exception as e:
            self.log_entries.append({'Error': f"Failed to process event: {str(e)}"})

    def write_to_file(self):
        try:
            with open(self.output_file, 'w') as f:
                # Add a header to the log file
                f.write(f"Log File Initialized: {datetime.now().isoformat()}\n\n")
                for entry in self.log_entries:
                    # Write each entry in a readable format
                    f.write(json.dumps(entry, indent=4) + "\n\n")
        except Exception as e:
            print(f"Error writing log file: {e}")

# Usage example:
# processor = LogProcessor("output_log.txt")
# for event in events_list:  # Replace with actual list of events
#     processor.process_event(event)
# processor.write_to_file()