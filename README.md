\# Financial Document Analyzer - Debugged Version



A comprehensive financial document analysis system built with CrewAI that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents.



\## 📋 Assignment Overview



This repository contains the debugged version of the Financial Document Analyzer for the VWO Generative AI Internship assignment. The original codebase had multiple bugs and inefficient prompts that have been identified and fixed.



\## 🐛 Bugs Found and Fixed



\### Deterministic Bugs



| Bug | Location | Fix |

|-----|----------|-----|

| \*\*Missing FastAPI imports\*\* | `main.py` | Added proper import statements and installed required packages |

| \*\*Incorrect CrewAI Tool imports\*\* | `tools.py` | Changed from `from crewai\_tools import tool` to proper BaseTool inheritance |

| \*\*Tool class validation errors\*\* | `tools.py` | Created proper Tool classes with BaseTool inheritance for CrewAI compatibility |

| \*\*Missing template variables\*\* | `tasks.py` | Removed complex context dependencies like `{verify\_document\_output}` that caused CrewAI validation errors |

| \*\*Agent memory configuration\*\* | `agents.py` | Disabled memory features that required OpenAI embeddings when using Gemini |

| \*\*Model name errors\*\* | `agents.py` | Updated deprecated `gemini-1.5-flash` to current `gemini-2.5-flash` |

| \*\*LLM initialization failure\*\* | `agents.py` | Fixed `convert\_system\_message\_to\_human` parameter and proper ChatGoogleGenerativeAI import |

| \*\*Environment variable handling\*\* | `.env.example` | Added proper template for API keys with clear instructions |

| \*\*File upload path issues\*\* | `main.py` | Created uploads directory and proper file cleanup after processing |

| \*\*Import path errors\*\* | Multiple files | Fixed relative imports to use correct module names |



\### Inefficient Prompts Fixed



| Original Issue | Fixed Solution |

|----------------|----------------|

| Vague instructions like "analyze this document" | Specific extraction requirements for financial metrics |

| No output format specification | Defined JSON structure for all responses |

| Missing context for agents | Added clear role definitions and backstories |

| Contradictory requirements | Removed conflicting instructions |

| No error handling guidance | Added null value handling for missing data |

| Overly complex task dependencies | Simplified to use only `{file\_path}` and `{query}` variables |



\## 🚀 Setup Instructions



\### Prerequisites



\- Python 3.10 or higher

\- Git

\- Google Gemini API key (free from \[Google AI Studio](https://aistudio.google.com))



\### Installation Steps



1\. \*\*Clone the repository\*\*

&nbsp;  ```bash

&nbsp;  git clone https://github.com/varshitharevelli/financial-document-analyzer-debug.git

&nbsp;  cd financial-document-analyzer-debug

