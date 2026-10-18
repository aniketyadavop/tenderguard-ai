import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, CheckCircle2, Building, Eye, EyeOff } from 'lucide-react';
import './LoginPage.css';

export default function LoginPage({ onLogin, onGuestLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState('evaluator'); // 'evaluator' | 'vendor'

  const handleSubmit = (e) => {
    e.preventDefault();
    const userRole = role === 'evaluator' ? 'Procurement Officer' : 'Bidding Vendor';
    const userName = email ? email.split('@')[0] : (role === 'evaluator' ? 'S. Sharma (Evaluator)' : 'TechNova Bidder');
    onLogin({
      name: userName,
      role: userRole,
      isGuest: false,
      email: email || 'officer@gem.gov.in'
    });
  };

  const handleGuest = () => {
    onGuestLogin({
      name: 'Guest Auditor',
      role: 'Guest / Demo Access',
      isGuest: true,
      email: 'guest@tenderguard.local'
    });
  };

  return (
    <div className="login-page-container">
      {/* Background Decorative Grid */}
      <div className="login-bg-grid"></div>

      <div className="login-card">
        {/* Brand Header */}
        <div className="login-brand-header">
          <div className="login-logo-wrap">
            <img 
              src="/tenderguard-logo.jpg" 
              alt="TenderGuard Logo" 
              className="login-brand-logo" 
            />
          </div>
          <h1 className="login-title">Sign in to TenderGuard AI</h1>
          <p className="login-subtitle">
            Secure, Explainable Compliance Verification for Public Procurement
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="role-selector">
          <button 
            type="button" 
            className={`role-tab ${role === 'evaluator' ? 'role-active' : ''}`}
            onClick={() => setRole('evaluator')}
          >
            <Shield size={16} />
            <span>Procurement Officer</span>
          </button>
          <button 
            type="button" 
            className={`role-tab ${role === 'vendor' ? 'role-active' : ''}`}
            onClick={() => setRole('vendor')}
          >
            <Building size={16} />
            <span>Bidding Vendor</span>
          </button>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">
              {role === 'evaluator' ? 'Government / GeM Email ID' : 'Company Email ID'}
            </label>
            <div className="input-field-wrap">
              <User size={16} className="input-icon" />
              <input 
                type="email" 
                className="form-input" 
                placeholder={role === 'evaluator' ? 'officer.nic@gem.gov.in' : 'compliance@technova.com'}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <div className="password-label-row">
              <label className="form-label">Password / Security PIN</label>
              <button 
                type="button" 
                className="forgot-btn"
                onClick={() => alert('Demo Mode: You can enter any password or click "Continue as Guest".')}
              >
                Forgot PIN?
              </button>
            </div>
            <div className="input-field-wrap">
              <Lock size={16} className="input-icon" />
              <input 
                type={showPassword ? 'text' : 'password'} 
                className="form-input" 
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button 
                type="button" 
                className="pwd-toggle-btn" 
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" className="login-submit-btn">
            <span>Sign In to Audit Workspace</span>
            <ArrowRight size={16} />
          </button>
        </form>

        {/* Divider */}
        <div className="login-divider">
          <span>OR</span>
        </div>

        {/* Continue as Guest Button */}
        <div className="guest-action-block">
          <button 
            type="button" 
            className="guest-login-btn"
            onClick={handleGuest}
            id="btn-guest-login"
          >
            <span className="guest-badge">Instant Demo</span>
            <span className="guest-label">Continue as Guest</span>
            <span className="guest-sub">Full access without signing in · Preloaded audit files</span>
          </button>
        </div>

        {/* Security / Compliance Badges */}
        <div className="login-footer-security">
          <div className="security-item">
            <CheckCircle2 size={13} className="sec-icon" />
            <span>GFR 2017 & GeM 4.0 Standard</span>
          </div>
          <div className="security-item">
            <Lock size={13} className="sec-icon" />
            <span>Zero-Retention Ephemeral Privacy</span>
          </div>
        </div>
      </div>
    </div>
  );
}
