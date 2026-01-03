// SQL Query Utilities
// Shared utilities for safe SQL query manipulation

const SQLUtils = {
    /**
     * Safely extracts conditions from a WHERE clause
     * @param {string} whereClause - The WHERE clause string (may start with "WHERE ")
     * @returns {string} - Just the conditions without "WHERE "
     */
    extractWhereConditions: (whereClause) => {
        if (!whereClause) return '';
        const whereMatch = whereClause.match(/^WHERE\s+(.+)$/i);
        return whereMatch ? whereMatch[1].trim() : whereClause.trim();
    },
    
    /**
     * Safely injects WHERE conditions into a SQL query
     * @param {string} sql - The original SQL query
     * @param {string} conditions - The conditions to inject (without WHERE keyword)
     * @returns {string} - Modified SQL with conditions injected
     */
    injectWhereConditions: (sql, conditions) => {
        if (!conditions || !conditions.trim()) return sql;
        
        const trimmedSQL = sql.trim();
        const trimmedConditions = conditions.trim();
        
        // Check if SQL already has a WHERE clause
        if (/\bWHERE\b/i.test(trimmedSQL)) {
            // Find the position right after WHERE keyword
            const whereMatch = trimmedSQL.match(/\bWHERE\b\s*/i);
            if (whereMatch) {
                const whereEndPos = whereMatch.index + whereMatch[0].length;
                // Insert new conditions right after WHERE, before existing conditions
                return trimmedSQL.slice(0, whereEndPos) + 
                       trimmedConditions + ' AND ' + 
                       trimmedSQL.slice(whereEndPos);
            }
            // Fallback: just return original if we can't find WHERE (shouldn't happen)
            return trimmedSQL;
        } else {
            // No WHERE clause exists, add one before GROUP BY, ORDER BY, or LIMIT
            const insertMatch = trimmedSQL.match(/\b(GROUP BY|ORDER BY|LIMIT)\b/i);
            if (insertMatch) {
                const insertPos = insertMatch.index;
                return trimmedSQL.slice(0, insertPos) + 
                       'WHERE ' + trimmedConditions + '\n' + 
                       trimmedSQL.slice(insertPos);
            } else {
                // No GROUP BY, ORDER BY, or LIMIT found, add at end
                return trimmedSQL + '\nWHERE ' + trimmedConditions;
            }
        }
    },
    
    /**
     * Validates that a value is a safe positive integer
     * @param {any} value - The value to validate
     * @returns {number|null} - Validated integer or null if invalid
     */
    sanitizeNumber: (value) => {
        const num = Number(value);
        return (!isNaN(num) && isFinite(num) && num >= 0) ? Math.floor(num) : null;
    },
    
    /**
     * Validates that a value is in a whitelist of allowed enum values
     * @param {any} value - The value to validate
     * @param {string[]} allowedValues - Array of allowed values
     * @returns {string|null} - Validated value or null if not in whitelist
     */
    validateEnum: (value, allowedValues) => {
        const strValue = String(value).toLowerCase();
        return allowedValues.includes(strValue) ? strValue : null;
    }
};
