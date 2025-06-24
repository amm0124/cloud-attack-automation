import React, { useState, useRef } from 'react';
import Layout from '../../../components/layout/Layout';
import './NmapCollectPage.css';

function NmapCollectPage() {
    const [logs, setLogs] = useState('');
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [showDownloadBtn, setShowDownloadBtn] = useState(false);
    const outputRef = useRef(null);
    const wsRef = useRef(null);

    const startScan = () => {
        const ipAddress = document.getElementById('target').value;
        const output = document.getElementById('output');

        // 상태 초기화
        setLogs('');
        setDownloadUrl(null);
        setShowDownloadBtn(false);

        // 이전 연결이 있으면 종료
        if (wsRef.current) {
            wsRef.current.close();
        }

        // 새 WebSocket 연결 생성
        const ws = new WebSocket('ws://localhost:8000/ws/collecting/nmap');
        wsRef.current = ws;

        ws.onopen = () => {
            ws.send(JSON.stringify({
                target_ip_range: ipAddress
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'log') {
                setLogs(prev => prev + data.message + '\n');
                // 로그 스크롤 자동 조정
                if (outputRef.current) {
                    setTimeout(() => {
                        outputRef.current.scrollTop = outputRef.current.scrollHeight;
                    }, 10);
                }
            } else if (data.type === 'download_url') {
                setDownloadUrl(data.url);
                setShowDownloadBtn(true);
            } else if (data.type === 'error') {
                setLogs(prev => prev + '❌ 오류: ' + data.message + '\n');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
            setLogs(prev => prev + '❌ 연결 오류가 발생했습니다.\n');
        };
    };

    const downloadReport = () => {
        if (downloadUrl) {
            const fullUrl = 'http://localhost:8000' + downloadUrl;
            window.open(fullUrl, '_blank');
        }
    };

    return (
        <Layout>
            <div className="scanning-page">
                <h2>Nmap 스캐닝을 통한 IP 주소 정보 수집</h2>
                <p className="page-description">Nmap 스캔을 통해 특정 IP 주소에 대한 정보 수집후 보고서 형태로 도출합니다</p>

                <div className="scan-form">
                    <div className="form-group">
                        <label htmlFor="target">스캔 대상 IP 주소</label>
                        <input
                            type="text"
                            id="target"
                        />
                    </div>

                    <div className="button-group">
                        <button className="start-btn" onClick={startScan}>스캔 시작</button>

                        {showDownloadBtn && (
                            <button
                                className="download-btn"
                                onClick={downloadReport}
                            >
                                📄 보고서 다운로드
                            </button>
                        )}
                    </div>
                </div>

                <pre id="output" className="output-container" ref={outputRef}>{logs}</pre>
            </div>
        </Layout>
    );
}

export default NmapCollectPage;