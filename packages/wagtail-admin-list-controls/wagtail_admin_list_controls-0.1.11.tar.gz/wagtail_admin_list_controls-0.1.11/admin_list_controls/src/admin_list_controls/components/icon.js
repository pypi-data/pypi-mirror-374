import React from 'react';
import c from 'classnames';

export function Icon({ control }) {
    // Always render modern Wagtail SVG (icon_name is required)
    return (
        <svg
            className={c(
                'alc__icon',
                'icon',
                `icon-${control.icon_name}`,
                'icon'
            )}
            style={control.style}
            aria-hidden='true'
        >
            <use href={`#icon-${control.icon_name}`}></use>
        </svg>
    );
}
