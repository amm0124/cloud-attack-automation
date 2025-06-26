// src/pages/index.js
import React, {useRef, useState} from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../../components/layout/Layout';
import './DirectLambdaStopAttackPage.css.css';


function DirectLambdaStopAttackPage() {
    const [logs, setLogs] = useState('');
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [showDownloadBtn, setShowDownloadBtn] = useState(false);
    const outputRef = useRef(null);
    const wsRef = useRef(null);

    const startScan = () => {
        const accessKey = document.getElementById('access-key').value;
        const secretKey = document.getElementById('secret-key').value;
        const region = document.getElementById('region').value;
        const functionName = document.getElementById('function-name').value;

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
        const ws = new WebSocket('ws://localhost:8000/ws/attacks/direct/lambda-injection');
        wsRef.current = ws;

        ws.onopen = () => {
            // GitHub URL 전송
            ws.send(JSON.stringify({
                access_key: accessKey,
                secret_key: secretKey,
                region: region,
                function_name: functionName,
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
                setLogs(prev => prev + '오류: ' + data.message + '\n');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
            setLogs(prev => prev + '연결 오류가 발생했습니다.\n');
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
                <h2>Lambda 삭제</h2>
                <p className="page-description">AWS Lambda를 삭제합니다.</p>

                <div className="scan-form">
                    <div className="form-group">
                        <label htmlFor="target">Access Key</label>
                        <input
                            type="text"
                            id="access-key"
                            placeholder="Access Key"
                        />
                    </div>


                    <div className="form-group">
                        <label htmlFor="target">Secret Key</label>
                        <input
                            type="text"
                            id="secret-key"
                            placeholder="Secret Key"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="target">Region</label>
                        <input
                            type="text"
                            id="region"
                            placeholder="Region"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="target">lambda function name</label>
                        <input
                            type="text"
                            id="function-name"
                            placeholder="lambda function name"
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

export default DirectLambdaStopAttackPage;
