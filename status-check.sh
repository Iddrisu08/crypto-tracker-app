#!/bin/bash

echo "🔍 Crypto Tracker Status Check"
echo "================================"

# Check backend server
echo "📡 Backend Server (Port 5001):"
if curl -s http://127.0.0.1:5001/portfolio > /dev/null; then
    echo "✅ Backend server is running and responsive"
    echo "   📊 Total portfolio value: $(curl -s http://127.0.0.1:5001/portfolio | jq -r '.total_value // "N/A"')"
else
    echo "❌ Backend server is not responding"
    echo "   💡 Try: cd crypto-tracker-backend && python3 app.py"
fi

echo ""

# Check frontend server
echo "🌐 Frontend Server (Port 5173):"
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend server is running"
else
    echo "❌ Frontend server is not responding"
    echo "   💡 Try: cd crypto-tracker-frontend && npm run dev"
fi

echo ""

# Check performance metrics endpoint
echo "📈 Analytics Endpoint:"
if curl -s http://127.0.0.1:5001/performance_metrics > /dev/null; then
    echo "✅ Performance metrics endpoint is working"
    echo "   📊 ROI: $(curl -s http://127.0.0.1:5001/performance_metrics | jq -r '.total_metrics.roi_percent // "N/A"')%"
else
    echo "❌ Performance metrics endpoint is not working"
fi

echo ""

# Check processes
echo "🔧 Process Status:"
BACKEND_PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}' | head -1)
FRONTEND_PID=$(ps aux | grep "node.*vite" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$BACKEND_PID" ]; then
    echo "✅ Backend process running (PID: $BACKEND_PID)"
else
    echo "❌ No backend process found"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    echo "✅ Frontend process running (PID: $FRONTEND_PID)"
else
    echo "❌ No frontend process found"
fi

echo ""
echo "🔗 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://127.0.0.1:5001"
echo "   Portfolio Analytics should now be working! 🎉"