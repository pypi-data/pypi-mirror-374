// Supabase Configuration for Email Notifications
// Replace with your actual Supabase project details

const SUPABASE_CONFIG = {
    url: 'https://cisfekmvzlyctbnnnuid.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpc2Zla212emx5Y3Ribm5udWlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4OTM3NTMsImV4cCI6MjA3MjQ2OTc1M30.P9yGG0K5ZPVc-DapHN8yG2qX0rbBmbqr-SXVF3uekJk'
};

// Initialize Supabase client (uncomment when you have Supabase set up)

import { createClient } from '@supabase/supabase-js';
const supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);


// Example function to save email notification to Supabase
async function saveEmailNotification(notificationData) {
    try {
        // Uncomment when Supabase is set up
        
        const { data, error } = await supabase
            .from('email_notifications')
            .insert([notificationData]);

        if (error) {
            console.error('Error saving to Supabase:', error);
            return { success: false, error };
        }

        return { success: true, data };
        

        // For now, just log the data
        console.log('Email notification data:', notificationData);
        return { success: true, data: notificationData };

    } catch (error) {
        console.error('Error in saveEmailNotification:', error);
        return { success: false, error };
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { saveEmailNotification, SUPABASE_CONFIG };
}