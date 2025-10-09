"""
JSON to List Conversion Node
Converts a JSON string containing a list into a Python list object.
"""
import json

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode


class JsonToList(DataNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.category = "Data"
        self.description = "Convert JSON string containing a list to Python list object"
        
        # Input JSON parameter
        self.add_parameter(
            Parameter(
                name="json_input",
                input_types=["str", "json"],
                type="str",
                tooltip="JSON string or JSON data containing a list. Examples:\n• Simple: [1, 2, 3]\n• Strings: [\"item1\", \"item2\", \"item3\"]\n• Mixed: [\"text\", 42, true, null]\n• Formatted:\n[\n  \"first_item\",\n  \"second_item\",\n  \"third_item\"\n]",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={
                    "multiline": True, 
                    "placeholder_text": "[\n  \"first_item\",\n  \"second_item\",\n  \"third_item\"\n]"
                }
            )
        )
        
        # Output list parameter
        self.add_parameter(
            Parameter(
                name="list_output",
                output_type="list[Any]",
                type="list[Any]",
                tooltip="The parsed Python list from the JSON input",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"is_full_width": True}
            )
        )
        
        # Status parameter for feedback
        self.add_parameter(
            Parameter(
                name="status",
                output_type="str",
                type="str",
                tooltip="Processing status and validation info",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"hide": True}
            )
        )
    
    def process(self) -> None:
        """Convert JSON string or JSON data to Python list."""
        json_input = self.get_parameter_value("json_input")
        
        if json_input is None:
            self.parameter_output_values["list_output"] = []
            self.parameter_output_values["status"] = "⚠️ Empty input - returning empty list"
            self.publish_update_to_parameter("status", "⚠️ Empty input - returning empty list")
            return
        
        # Handle string inputs (check for empty strings)
        if isinstance(json_input, str) and json_input.strip() == "":
            self.parameter_output_values["list_output"] = []
            self.parameter_output_values["status"] = "⚠️ Empty input - returning empty list"
            self.publish_update_to_parameter("status", "⚠️ Empty input - returning empty list")
            return
        
        try:
            # Handle different input types
            if isinstance(json_input, str):
                # Parse JSON string
                parsed_data = json.loads(json_input)
            else:
                # Assume it's already parsed JSON data
                parsed_data = json_input
            
            # Validate that the result is a list
            if not isinstance(parsed_data, list):
                self.parameter_output_values["list_output"] = []
                error_msg = f"❌ Input does not contain a list. Found: {type(parsed_data).__name__}"
                self.parameter_output_values["status"] = error_msg
                self.publish_update_to_parameter("status", error_msg)
                raise ValueError(f"Input must be a list, but got {type(parsed_data).__name__}")
            
            # Set the output
            self.parameter_output_values["list_output"] = parsed_data
            
            # Provide status feedback
            list_length = len(parsed_data)
            if list_length == 0:
                status_msg = "✅ Converted to empty list"
            elif list_length == 1:
                status_msg = "✅ Converted to list with 1 item"
            else:
                status_msg = f"✅ Converted to list with {list_length} items"
            
            # Include type information for first few items
            if parsed_data:
                sample_types = []
                for i, item in enumerate(parsed_data[:3]):  # Show types of first 3 items
                    sample_types.append(f"• {type(item).__name__}")
                
                if len(parsed_data) > 3:
                    type_info = f"\n• Item types:\n{chr(10).join(sample_types)}\n• ..."
                else:
                    type_info = f"\n• Item types:\n{chr(10).join(sample_types)}"
                
                status_msg += type_info
            
            self.parameter_output_values["status"] = status_msg
            self.publish_update_to_parameter("status", status_msg)
            
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors (only for string inputs)
            self.parameter_output_values["list_output"] = []
            error_msg = f"❌ Invalid JSON format: {str(e)}"
            self.parameter_output_values["status"] = error_msg
            self.publish_update_to_parameter("status", error_msg)
            raise ValueError(f"Failed to parse JSON: {str(e)}")
        
        except Exception as e:
            # Handle other errors
            self.parameter_output_values["list_output"] = []
            error_msg = f"❌ Error processing input: {str(e)}"
            self.parameter_output_values["status"] = error_msg
            self.publish_update_to_parameter("status", error_msg)
            raise Exception(f"Error converting to list: {str(e)}")
