import React from 'react';
import { useStore } from '../store';

export function SettingsPanel() {
    const { settings, updateSettings } = useStore();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        // Handle number inputs
        const isNumber = e.target.type === 'number';
        updateSettings({ [name]: isNumber ? parseFloat(value) : value });
    };

    return (
        <>
            <div className="panel-header">Settings</div>
            <div className="settings-content">
                <div className="form-group">
                    <label>Sigma_w (%)</label>
                    <input type="number" name="sigma_w" value={settings.sigma_w} onChange={handleChange} />
                </div>
                <div className="form-group">
                    <label>L_c (Correlation Length)</label>
                    <input type="number" name="L_c" value={settings.L_c} onChange={handleChange} step="0.001" />
                </div>
                <div className="form-group">
                    <label>Model</label>
                    <select name="model" value={settings.model} onChange={handleChange}>
                        <option value="exponential">Exponential</option>
                        <option value="gaussian">Gaussian</option>
                        <option value="matern32">Matern32</option>
                        <option value="band_limited">Band Limited</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>ds_arc</label>
                    <input type="number" name="ds_arc" value={settings.ds_arc} onChange={handleChange} step="0.0001" />
                </div>
                <div className="form-group">
                    <label>n_resample</label>
                    <input type="number" name="n_resample" value={settings.n_resample} onChange={handleChange} />
                </div>
                <div className="form-group">
                    <label>w_min (%)</label>
                    <input type="number" name="w_min" value={settings.w_min} onChange={handleChange} />
                </div>
                <div className="form-group">
                    <label>w_max (%)</label>
                    <input type="number" name="w_max" value={settings.w_max} onChange={handleChange} />
                </div>
            </div>
        </>
    );
}
