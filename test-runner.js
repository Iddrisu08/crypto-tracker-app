#!/usr/bin/env node

/**
 * Comprehensive Test Runner for Crypto Tracker
 * Runs all Playwright tests systematically
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';

class TestRunner {
  constructor() {
    this.results = {
      portfolio: { status: 'pending', output: '', exitCode: null },
      analytics: { status: 'pending', output: '', exitCode: null },
      transactions: { status: 'pending', output: '', exitCode: null },
      integration: { status: 'pending', output: '', exitCode: null }
    };
  }

  async runCommand(command, args, testName) {
    return new Promise((resolve, reject) => {
      console.log(`\n🧪 Running ${testName}...`);
      console.log(`Command: ${command} ${args.join(' ')}`);
      
      const child = spawn(command, args, {
        cwd: '/Users/iddrisuabdulrazakiddrisu/crypto-tracker-project/crypto-tracker-frontend',
        stdio: 'pipe'
      });

      let output = '';
      let errorOutput = '';

      child.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        process.stdout.write(text);
      });

      child.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        process.stderr.write(text);
      });

      child.on('close', (code) => {
        this.results[testName] = {
          status: code === 0 ? 'passed' : 'failed',
          output: output + errorOutput,
          exitCode: code
        };
        resolve(code);
      });

      child.on('error', (error) => {
        this.results[testName] = {
          status: 'error',
          output: error.message,
          exitCode: 1
        };
        reject(error);
      });
    });
  }

  async checkServers() {
    console.log('🔍 Checking server status...');
    
    try {
      const fetch = (await import('node-fetch')).default;
      
      // Check frontend
      try {
        await fetch('http://localhost:5173');
        console.log('✅ Frontend server is running on port 5173');
      } catch (e) {
        console.log('❌ Frontend server is not running. Please start with: npm run dev');
        return false;
      }

      // Check backend
      try {
        await fetch('http://127.0.0.1:5001/portfolio');
        console.log('✅ Backend server is running on port 5001');
      } catch (e) {
        console.log('❌ Backend server is not running. Please start with: python3 app.py');
        return false;
      }

      return true;
    } catch (e) {
      console.log('⚠️  Could not check servers (fetch not available)');
      return true; // Assume servers are running
    }
  }

  async runAllTests() {
    console.log('🚀 Starting Comprehensive Test Suite for Crypto Tracker');
    console.log('=======================================================');

    // Check if servers are running
    const serversRunning = await this.checkServers();
    if (!serversRunning) {
      process.exit(1);
    }

    try {
      // Test 1: Portfolio Features
      console.log('\n🔍 TEST 1: Portfolio Features');
      console.log('==============================');
      await this.runCommand('npx', ['playwright', 'test', 'tests/portfolio.spec.js', '--reporter=line'], 'portfolio');

      // Test 2: Analytics Dashboard
      console.log('\n📊 TEST 2: Analytics Dashboard');
      console.log('==============================');
      await this.runCommand('npx', ['playwright', 'test', 'tests/analytics.spec.js', '--reporter=line'], 'analytics');

      // Test 3: Transaction Management
      console.log('\n💰 TEST 3: Transaction Management');
      console.log('=================================');
      await this.runCommand('npx', ['playwright', 'test', 'tests/transactions.spec.js', '--reporter=line'], 'transactions');

      // Test 4: Full Integration
      console.log('\n🎯 TEST 4: Full Integration Test');
      console.log('===============================');
      await this.runCommand('npx', ['playwright', 'test', '--reporter=line'], 'integration');

    } catch (error) {
      console.error('❌ Test execution failed:', error);
    }

    // Generate summary
    this.generateSummary();
  }

  generateSummary() {
    console.log('\n📋 TEST SUMMARY');
    console.log('===============');

    const tests = [
      { name: 'Portfolio Tests', key: 'portfolio' },
      { name: 'Analytics Tests', key: 'analytics' },
      { name: 'Transaction Tests', key: 'transactions' },
      { name: 'Integration Tests', key: 'integration' }
    ];

    let totalPassed = 0;
    let totalFailed = 0;

    tests.forEach(test => {
      const result = this.results[test.key];
      if (result.status === 'passed') {
        console.log(`✅ ${test.name}: PASSED`);
        totalPassed++;
      } else if (result.status === 'failed') {
        console.log(`❌ ${test.name}: FAILED (Exit Code: ${result.exitCode})`);
        totalFailed++;
      } else {
        console.log(`⚠️  ${test.name}: ${result.status.toUpperCase()}`);
        totalFailed++;
      }
    });

    console.log('\n📊 Generating HTML Report...');
    spawn('npx', ['playwright', 'show-report', '--host=127.0.0.1', '--port=9323'], {
      cwd: '/Users/iddrisuabdulrazakiddrisu/crypto-tracker-project/crypto-tracker-frontend',
      detached: true,
      stdio: 'ignore'
    });

    console.log('\n🎉 Test Suite Complete!');
    console.log('=======================');
    console.log('📊 View detailed report at: http://127.0.0.1:9323');
    console.log('📁 Test artifacts saved in: playwright-report/');
    console.log('🎥 Screenshots and videos available for failed tests');

    if (totalFailed === 0) {
      console.log('🎉 ALL TESTS PASSED! Your crypto tracker is working perfectly! 🚀');
      process.exit(0);
    } else {
      console.log(`⚠️  ${totalFailed} test suite(s) failed. Check the report for details.`);
      process.exit(1);
    }
  }
}

// Run the test suite
const runner = new TestRunner();
runner.runAllTests().catch(console.error);