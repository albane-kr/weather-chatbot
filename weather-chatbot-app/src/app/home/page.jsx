'use client'

import React from 'react';
import styles from '@/app/page.module.css';

export default function Home() {

    const sendButton = "sendButton";

    return (
        <div className={styles.page}>
            <header>
                <h1 className={styles.header}>RAINY Reacting According to Incoming Nature's Yearnings</h1>
            </header>
            <main className={styles.main}>
                <div className={styles.column}>
                    <p>Welcome to rAIny - the weather chatbot. Ask me anything about the weather!</p>
                </div>
                <div className={styles.column}>
                    <header>
                        <h2>Chat with rAIny</h2>
                    </header>
                    <ul className={styles.chatbot}>
                        <li className={`${styles.chat_incoming} ${styles.chat}`}>
                            <p>Moien! How can I help you?</p>
                        </li>
                    </ul>
                    <div className={styles.chat_input}>
                        <div>
                            <textarea placeholder="Enter a message..."/>
                        </div>
                        <div>
                            <button id= {sendButton}/>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}