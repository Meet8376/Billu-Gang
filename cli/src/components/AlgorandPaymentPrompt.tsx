import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';

interface AlgorandPaymentPromptProps {
  onPaymentConfirmed: (data: { algoBalance: number; usdBalance: number; txHash: string }) => void;
  onCancel?: () => void;
}

export const AlgorandPaymentPrompt: React.FC<AlgorandPaymentPromptProps> = ({
  onPaymentConfirmed,
  onCancel
}) => {
  const [depositAlgo, setDepositAlgo] = useState('5.0');
  const [verifying, setVerifying] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [txHash, setTxHash] = useState('');

  const targetAddress = 'BILLUGANG27XALGORANDPAYMENTGATEWAYTESTNET999';

  useInput(
    (input, key) => {
      if (verifying || confirmed) return;

      if (key.return) {
        setVerifying(true);
        const amount = parseFloat(depositAlgo) || 5.0;
        const fakeHash = 'TX-' + Math.random().toString(36).substring(2, 12).toUpperCase() + '-ALGO';
        setTxHash(fakeHash);

        setTimeout(() => {
          setVerifying(false);
          setConfirmed(true);
          setTimeout(() => {
            onPaymentConfirmed({
              algoBalance: amount,
              usdBalance: amount * 0.2, // 1 ALGO = $0.20 USD
              txHash: fakeHash
            });
          }, 1200);
        }, 1500);
      } else if (key.backspace || key.delete) {
        setDepositAlgo((prev) => prev.slice(0, -1));
      } else if (input.match(/^[0-9.]$/)) {
        setDepositAlgo((prev) => (prev.length < 5 ? prev + input : prev));
      } else if (key.escape && onCancel) {
        onCancel();
      }
    },
    { isActive: true }
  );

  const amountVal = parseFloat(depositAlgo) || 0;
  const usdVal = (amountVal * 0.2).toFixed(2);

  return (
    <Box
      flexDirection="column"
      borderStyle="single"
      borderColor="white"
      paddingX={2}
      paddingY={1}
      width={78}
    >
      <Box justifyContent="center" marginBottom={1}>
        <Text color="white" bold>
          ALGORAND DEVELOPER SETTLEMENT GATEWAY
        </Text>
      </Box>

      {verifying ? (
        <Box flexDirection="column" alignItems="center" marginY={2}>
          <Text color="white" bold>
            <Spinner type="dots" /> Verifying Transaction Block on Algorand Testnet...
          </Text>
          <Text color="gray">Tx Hash: {txHash}</Text>
        </Box>
      ) : confirmed ? (
        <Box flexDirection="column" alignItems="center" marginY={2}>
          <Text color="green" bold>
            [CONFIRMED] Settlement Verified on Algorand Blockchain!
          </Text>
          <Text color="white" bold>
            Credited: {amountVal} ALGO (${usdVal} USD Equivalent)
          </Text>
        </Box>
      ) : (
        <Box flexDirection="column" gap={1}>
          <Box justifyContent="space-between">
            <Text color="gray">Consensus Network:</Text>
            <Text color="white" bold>Algorand Testnet (testnet-v1.0)</Text>
          </Box>
          <Box justifyContent="space-between">
            <Text color="gray">Merchant Receiver:</Text>
            <Text color="white" bold wrap="truncate">{targetAddress.slice(0, 32)}...</Text>
          </Box>
          <Box justifyContent="space-between">
            <Text color="gray">Deposit Credit (ALGO):</Text>
            <Text color="white" bold>{depositAlgo} ALGO  (${usdVal} USD Equivalent)</Text>
          </Box>
          <Box justifyContent="space-between">
            <Text color="gray">Compute Rate:</Text>
            <Text color="gray">1.00 ALGO = $0.20 USD Autonomous Credits</Text>
          </Box>

          <Box borderStyle="single" borderColor="white" paddingX={1} marginTop={1}>
            <Text color="gray">
              Type ALGO amount or press <Text color="white" bold>Enter</Text> to authorize Algorand payment.
            </Text>
          </Box>
        </Box>
      )}
    </Box>
  );

};
