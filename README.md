# WhatsApp Chat Analyzer ⚡

> **The Story:** I was tired of texting people and waiting 6 hours for a response. So I built a tool that analyzes your WhatsApp chats and tells you the best time to message someone for the fastest response. Now I know exactly when to text for quick replies. Open sourcing it because I know I'm not alone in this pain.

## What It Does

Analyzes your exported WhatsApp chats and generates **programmer-style metrics** to help you understand:

- **Best time to message someone** - When do they actually reply fast?
- **P50, P90, P99 response times** - Treat your conversations like API endpoints
- **Response time heatmaps** - Visualize when people are most responsive
- **Who's carrying the conversation** - Conversation initiator tracking
- **Double text frequency** - How desperate are you when left on read?
- **Message patterns** - Who talks more, message lengths, emoji usage
- **Activity patterns** - Hourly/daily activity, late night messages, longest gaps

## Quick Start

### 1. Export Your WhatsApp Chat

**iPhone:** Open chat → Tap contact name → Export Chat → Without Media  
**Android:** Open chat → Three dots (⋮) → More → Export chat → Without media

### 2. Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run analyzer
python analyser.py "your_chat.txt"

# Custom output folder
python analyser.py "chat.txt" -o my_results
```

## Output

Generates **12 visualization charts**:

1. **Summary Stats** - Complete overview
2. **Response Time Percentiles** - P50/P90/P95/P99 metrics
3. **Response Time Heatmap** - Best hours to message
4. **Message Volume** - Who talks more
5. **Activity Patterns** - Peak hours & weekend vs weekday
6. **Conversation Initiators** - Who starts conversations
7. **Double Text Analysis** - Messages sent before getting response
8. **Message Length** - Long vs short messagers
9. **Emoji Usage** - Top emojis per person
10. **Question Frequency** - Who asks more questions
11. **Conversation Gaps** - Longest silence periods
12. **Daily Streak** - Activity timeline

All charts saved as high-quality PNG files in the `output/` folder.

## Example Insights
```
P50 Response Time: 12.3 minutes
P90 Response Time: 2.4 hours
P99 Response Time: 6.8 hours

Best time to message: 8-10pm (avg 4 min response)
Worst time to message: 2-4pm (avg 3.5 hour response)
```

## Requirements

- Python 3.7+
- pandas, matplotlib, seaborn, numpy, wordcloud

## Privacy

All analysis runs locally. No data leaves your machine. The tool only reads the text file you provide.

## Built with ❤️ by

[Pankaj Tanwar](https://twitter.com/the2ndfloorguy), and checkout his [other side-hustles](https://pankajtanwar.in/side-hustles)